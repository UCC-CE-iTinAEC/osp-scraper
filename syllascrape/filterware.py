import logging
import fnmatch
import re

from scrapy import signals
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)

def check_fitlers(filters, spider, request, reponse=None):
    """Check a list of filters

    The first filter to match is applied.

    Return True if allowed or False if denied. If no filters match at all, return False.
    """
    for f in filters:
        if f(spider, request, response):
            if f.action == "allow":
                return True
            elif f.action == "deny":
                return False
            else:
                raise ValueError("Unknown filter action %r" % f.action)

    return False # Deny by default


class Filter:

    __slots__ = ['action', # 'allow' or 'deny'
                 'pattern', # 'glob' or 'regex'
                 'scheme', # http, https, etc.
                 'path', # urlunquoted
                 'query', # a list of (key, value) patterns
                 'parameters', # probably useless
                 'fragment',
                 'hostname',
                 'port', # text pattern
                 'source_anchor', # from parent page
                 'file_type', # sniffed from mimetype
                 'max_depth', # 0 for infinite depth (w/ resets), positive integer for a depth limit
                 '_regex', # compiled regex
                 ]

    # XXX possible additions: max_length, response headers?

    def __init__(self, action, pattern='regex', scheme=None, path=None,
                 query=None, parameters=None, fragment=None, hostname=None, port=None,
                 source_anchor=None, file_type=None, max_depth=None):

        # check args for valid values; fill in reasonable defaults.
        # compile patterns with re.compile or fnmatch.translate
        pass


    def __call__(self, spider, request, response):
        # test against urlparse_cached(request) fields, request.meta and
        # additional things from response (file_type?) if needed. test in
        # order of likelihood of False result. Use parse_qsl on request.query
        pass