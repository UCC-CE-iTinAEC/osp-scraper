import logging

from scrapy import Request
from scrapy.exceptions import IgnoreRequest

from .filterware import check_filters

logger = logging.getLogger(__name__)


class FilterMiddleware(object):
    """Middleware to support filters in the downloading layer."""

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_request(self, request, spider):
        # some requests for files come from scrapy itself (robots.txt, etc.)
        if 'depth' not in request.meta:
            return

        allowed, filter = check_filters(spider.filters, request)

        if not allowed and not request.dont_filter:
            raise IgnoreRequest

        if filter.max_depth is None:
            # reset depth to zero
            request.meta['depth'] = 0

        return None # allow request
