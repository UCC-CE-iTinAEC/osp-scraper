import logging
import fnmatch
import re
import attr

from scrapy import signals
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)

def check_filters(filters, request, reponse=None):
    """Check a list of filters

    The first filter to match is applied. If no filters match at all, return (False, None).

    :rtype: tuple of (bool, Filter)
    :returns: True if allowed or False if denied, and the matching filter
    """
    for f in filters:
        if f(spider, request, response):
            if f.action == "allow":
                return (True, f)
            elif f.action == "deny":
                return (False, f)
            else:
                raise ValueError("Unknown filter action %r" % f.action)

    return (False, None) # Deny by default

def _positive(instance, attribute, value):
    """attr validator that accepts positive numbers."""
    if value <= 0:
        raise ValueError('%s must be strictly positive' % attibute.name)

def _one_of(allowed_values):
    """construct an attr validator that accepts only `allowed_values`"""

    def _valid(instance, attribute, value):
        if value not in allowed_values:
            raise ValueError('%s must be one of %r' % (value, allowed_values))

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
                 'file_type', # sniffed from mimetype
                 'max_depth', # None for infinite depth (w/ resets), positive integer for a depth limit
                 ]

    # configuration
    action = attr.ib(validator=_one_of({'allow', 'deny'}))
    pattern = attr.ib(validator=_one_of({'literal', 'glob', 'regex'}))
    invert = attr.ib(validator=attr.validators.instance_of(bool))

    # filters on request URL
    scheme = attr.ib(validator=attr.validators.instance_of(str))
    path = attr.ib(validator=attr.validators.instance_of(str))
    parameters = attr.ib(validator=attr.validators.instance_of(str))
    fragment = attr.ib(validator=attr.validators.instance_of(str))
    hostname = attr.ib(validator=attr.validators.instance_of(str))
    port = attr.ib(validator=attr.validators.instance_of(str))

    # other filters
    source_anchor = attr.ib(validator=attr.validators.instance_of(str))
    file_type = attr.ib(validator=attr.validators.instance_of(str))
    query = FIXME
    max_depth = attr.ib(convert=int,
                        validator=attr.validators.optional(_positive_int))

    # XXX possible additions: max_length, response headers?

    @classmethod
    def compile(cls, *args, **kwargs):
        self = cls(*args, **kwargs)

        # regexes to apply to URLs
        self._url_regexes = {x:self._compile_filter(getattr(self, x))
                                 for x in {'scheme', 'path', 'parameters', 'fragment', 'hostname', 'port'}}

        self._source_anchor_regex = self._compile_filter(self.source_anchor)
        self._file_type_regex = self._compile_filter(self.file_type)

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


    def __call__(self, request, response):
        url = urlparse_cached(request)

        ret = True

        for name, regex in self._url_regexes:
            if not regex.match(getattr(url, name)):
                ret = False
                break

        if ret: # still True
            if not self._source_anchor_regex.match(request.meta['source_anchor']):
                ret = False
            elif not self._file_type_regex.match(request.meta['file_type']):
                ret = False
            elif request.depth > self.max_depth:
                ret = False
            else:
                # tests on query
                pass

        return ret if not invert else not ret

        # test against urlparse_cached(request) fields, request.meta and
        # additional things from response (file_type?) if needed. test in
        # order of likelihood of False result. Use parse_qsl on request.query
        pass