import logging
import re

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
                yield request
            else:
                # we have a request

                # some requests for files come from scrapy itself (robots.txt, etc.)
                if 'depth' not in request.meta or request.dont_filter:
                    yield request

                allowed, filter = check_filters(spider.filters, request)

                if not allowed:
                    pass # drop request
                else:
                    if filter.max_depth == None:
                        request.depth = 0 # reset depth

                    yield request # allow request

