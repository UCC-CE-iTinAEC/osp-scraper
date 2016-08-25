import logging
import fnmatch
import re
from urllib.parse import parse_qs
import attr


from scrapy import signals
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)

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
    # XXX it be nice to use slots here for performance, but we need
    # non-attr.ib attributes to hold compiled regexes. This could probably be
    # done through a base class holding the attr.ib's and a public subclass
    # doing instropection on it and adding new slots. Or something.

    WHATEVER = ['action', # 'allow' or 'deny'
                 'pattern', # 'glob', 'regex', or 'literal'
                 'scheme', # http, https, etc.
                 'path', # urlunquoted
                 'query', # a list of (key, value) patterns
                 'parameters', # probably useless
                 'fragment',
                 'hostname',
                 'port', # text pattern
                 'source_anchor', # from parent page
                 'max_depth', # None for infinite depth (w/ resets), positive integer for a depth limit
                 ]

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
                query = parse_qs(url.query)
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
