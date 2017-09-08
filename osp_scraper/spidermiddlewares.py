import logging

from scrapy import Request

from .filterware import check_filters

logger = logging.getLogger(__name__)


class FilterMiddleware(object):
    """Middleware to support filters in the spider layer
    """

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_spider_output(self, response, result, spider):
        for request in result:
            if not isinstance(request, Request):
                # Always allow objects that aren't Requests (dict or Item).
                yield request
            elif 'depth' not in request.meta:
                # Always allow requests for files that come from scrapy itself
                # (robots.txt, etc.).
                yield request
            elif request.dont_filter:
                # Don't filter requests with request.dont_filter.
                yield request
            else:
                # We have a request that needs to be checked against filters.
                allowed, filter = check_filters(spider.filters, request)

                if not allowed:
                    # Request not allowed by filter.
                    pass
                else:
                    # Request allowed by filter.
                    if filter.max_depth == None:
                        # Reset depth.
                        request.depth = 0

                    yield request

