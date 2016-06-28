import logging

from scrapy import signals
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)


class PrefixMiddleware(object):
    """
    Path prefix middleware. Based on from scrapy.spidermiddlewares.offsite.OffsiteMiddleware

    On each spider, set `allowed_paths` to a list of path prefixes, like so:

        allowed_domains = ['diploma-mill.edu']
        allowed_paths = [
            '/physics/syllabus/',
            '/chemistry/classes/',
            '/legacy-IT-dept/syllabus.exe',
        ]

    By default, all paths are allowed: `allowed_paths = ['/']`
    """
    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def process_spider_output(self, response, result, spider):
        for x in result:
            if isinstance(x, Request):
                if x.dont_filter or self.should_follow(x, spider):
                    yield x
                else:
                    path = urlparse_cached(x).path
                    if path not in self.paths_seen:
                        self.paths_seen.add(path)
                        logger.debug("Filtered offsite request to %(path)r: %(request)s",
                                     {'path': path, 'request': x}, extra={'spider': spider})
                        self.stats.inc_value('offsite/paths', spider=spider)
                    self.stats.inc_value('offsite/filtered', spider=spider)
            else:
                yield x

    def should_follow(self, request, spider):
        path = urlparse_cached(request).path
        return any(path.startswith(p) for p in self.allowed_paths)

    def get_allowed_paths(self, spider):
        """Override this method to implement a different path policy"""
        getattr(spider, 'allowed_paths', ['/']) # allow all paths by default

    def spider_opened(self, spider):
        self.allowed_paths = self.get_allowed_paths(spider)
        self.paths_seen = set()
