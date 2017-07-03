import logging
import fnmatch
import re
import urllib.parse
import attr
import os

from scrapy import signals
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)

# a list of base domains to blacklist; subdomains blocked too
blacklist_domains = [
    'facebook.com',
    'reddit.com',
    'twitter.com',
    'linkedin.com',
    'wikipedia.org',
]

def make_filters(seed_urls):
    """Generate filters for a spider from a list of URLs.

    * Allow paths with matching prefix to infinite depth
    * Allow same hostname to max depth of 2
    * Allow other domains to max depth of 1

    Args:
        seed_urls (list)
    """
    if not seed_urls:
        raise ValueError("List of URLs must be non-empty")

    filters = []

    blacklist_re = r"(^.*\.)?({})$".format(
        "|".join(map(re.escape, blacklist_domains))
    )

    # blacklist domains
    filters.append(
        Filter.compile(
            'deny',
            pattern='regex',
            hostname=blacklist_re
        )
    )

    # merge parameters from several seed urls, with unique domains & paths
    for url in seed_urls:
        u = urllib.parse.urlparse(url)
        # XXX: We should probably find a cleaner (and more extensive) approach
        # for checking against problematic strings in `seed_urls`.  For example,
        # we might want to check for a top-level domain.
        if not u.hostname:
            msg = "URL '{0}' does not have a hostname.  No filters will be made."
            logger.info(msg.format(url))
            continue

        prefix = re.escape(
            u.path if u.path.endswith('/') else os.path.dirname(u.path) + '/'
        )
        hostname = re.escape(u.hostname)
        port = re.escape(str(u.port)) if u.port else None

        # allow prefix to infinite depth
        filters.append(
            Filter.compile(
                'allow',
                pattern='regex',
                hostname=hostname,
                port=port,
                path=prefix + ".*"
            )
        )

        # allow same hostname to max depth 2
        filters.append(
            Filter.compile(
                'allow',
                pattern='regex',
                hostname=hostname,
                port=port,
                max_depth=2
            )
        )

    # allow other domains w/ max depth 1
    filters.append(Filter.compile('allow', max_depth=1))

    return filters

def check_filters(filters, request):
    """Check a list of filters

    The first filter to match is applied. If no filters match at all, return (False, None).

    :rtype: tuple of (bool, Filter)
    :returns: True if allowed or False if denied, and the matching filter
    """
    for f in filters:
        if f(request):
            if f.action == "allow":
                return (True, f)
            elif f.action == "deny":
                return (False, f)
            else:
                raise ValueError("Unknown filter action %r" % f.action)

    return (False, None) # Deny by default

## attr validators for internal use in Filter

def _positive_int(instance, attribute, value):
    """attr validator that accepts positive ints"""
    if not isinstance(value, int) or value <= 0:
        raise ValueError('%s must be a strictly positive int' % attribute.name)

def _one_of(allowed_values):
    """construct an attr validator that accepts only `allowed_values`"""

    def _valid(instance, attribute, value):
        if value not in allowed_values:
            raise ValueError('%s must be one of %r' % (value, allowed_values))

def _dict_of_str_str(instance, attribute, value):
    """attr validator that accepts dict of str => str"""
    if not isinstance(value, dict):
        raise TypeError('%s must be a dict' % attribute.name)

    for k, v in value.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise TypeError('%s must contain strings', attribute.name)

# an optional string attr validator
_optional_str = attr.validators.optional(attr.validators.instance_of(str))

@attr.s(cmp=False)
class Filter:
    """A filter for Requests.

    Construct instances of this class using :method:`compile` classmethod,
    *not* the usual `__init__`. Calling the filter object will return True if
    it matches.

    Filters are composed of multiple string-based patterns; all patterns must
    match for the filter to be accepted. The `query` field is a dict of
    `query paramter name => pattern`; extra parameters are ignored.

    Patterns may be None (the default), meaning that field is ignored; for
    the `max_depth` field, this means infinite depth.

    :ivar action: 'allow' or 'deny'
    :ivar pattern: how to interpret patterns: 'glob', 'regex', or 'literal'
    :ivar invert: invert the match conditions
    :ivar scheme: http, https, etc.
    :ivar path: path component, unquoted
    :ivar query:  dict of query parameter patterns
    :ivar parameters: parameter component; rarely used
    :ivar fragment: client-side fragment
    :ivar hostname: server domain
    :ivar port: server port, as text
    :ivar source_anchor: anchor text from parent page, lower cased
    :ivar max_depth:  None for infinite depth, positive integer for a depth limit
    """

    # XXX it be nice to use slots here for performance, but we need
    # non-attr.ib attributes to hold compiled regexes. This could probably be
    # done through a base class holding the attr.ib's and a public subclass
    # doing instropection on it and adding new slots. Or something.

    # configuration
    action = attr.ib(validator=_one_of({'allow', 'deny'}))
    pattern = attr.ib(validator=_one_of({'literal', 'glob', 'regex'}), default='regex')
    invert = attr.ib(validator=attr.validators.instance_of(bool), default=False)

    # filters on request URL
    scheme = attr.ib(validator=_optional_str, default=None)
    path = attr.ib(validator=_optional_str, default=None)
    parameters = attr.ib(validator=_optional_str, default=None)
    fragment = attr.ib(validator=_optional_str, default=None)
    hostname = attr.ib(validator=_optional_str, default=None)
    port = attr.ib(validator=_optional_str, default=None)

    # other filters
    source_anchor = attr.ib(validator=_optional_str, default=None)
    query = attr.ib(validator=attr.validators.optional(_dict_of_str_str), default=attr.Factory(dict))
    max_depth = attr.ib(validator=attr.validators.optional(_positive_int), default=None)

    def asdict(self):
        """return a dict representation of the filter"""
        return attr.asdict(self)

    @classmethod
    def compile(cls, *args, **kwargs):
        """primary constructor"""
        self = cls(*args, **kwargs)

        # regexes to apply to URLs
        self._url_regexes = {x: self._compile_filter(getattr(self, x))
                                 for x in {'scheme', 'path', 'parameters', 'fragment', 'hostname', 'port'}}

        self._source_anchor_regex = self._compile_filter(self.source_anchor)
        self._query_regexes = {k: self._compile_filter(v) for k, v in self.query.items()}
        return self

    def _compile_filter(self, s):
        if s is None:
            return None
        elif self.pattern == 'literal':
            regex = re.escape(s)
        elif self.pattern == 'glob':
            regex = fnmatch.translate(s)
        elif self.pattern == 'regex':
            regex = s

        return re.compile(regex)

    def __call__(self, request):
        url = urlparse_cached(request)

        ret = True

        for name, regex in self._url_regexes.items():
            if regex is not None and not regex.match(getattr(url, name) or ''):
                ret = False
                break

        if ret: # still True after above loop
            if (self._source_anchor_regex is not None and
                not self._source_anchor_regex.match(request.meta['source_anchor'].lower())):
                ret = False
            elif self.max_depth is not None and request.meta['depth'] > self.max_depth:
                ret = False
            else:
                # test all regexes in query_regexes, ignoring unknown query args from URL
                query = urllib.parse.parse_qs(url.query)
                for k, regex in self._query_regexes.items():
                    if not ret:
                        break # also break outer loop if we break out of inner one below
                    try:
                        l = query[k]
                    except KeyError:
                        # all keys must be present
                        ret = False
                        break
                    else:
                        # key present, test all args
                        for a in l:
                            if not regex.match(a):
                                ret = False
                                break # inner loop

        # return, inverting if necessary
        return ret if not self.invert else not ret
