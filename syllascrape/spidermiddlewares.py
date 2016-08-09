import logging
import re

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

    On each spider, set `external_path_max_depth` to a positive integer to
    enable crawling other paths to a limited depth. Defaults to zero.
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
            if not isinstance(x, Request):
                yield x
            else:
                # we have a request
                if x.dont_filter or self.should_follow(x, spider):
                    # path is explictly allowed, reset depth to zero
                    x.meta['path_depth'] = 0
                    yield x
                else:
                    depth = x.meta['path_depth']
                    if depth < self.external_path_max_depth:
                        # an external path with less than max depth; record stats & yield request
                        self.stats.inc_value('request_depth_count/%s' % depth, spider=spider)
                        self.stats.max_value('request_depth_max', depth, spider=spider)
                        yield x
                    else:
                        # external path crawled deeper than max depth; record stats & drop
                        path = urlparse_cached(x).path
                        if path not in self.paths_seen:
                            self.paths_seen.add(path)
                            logger.debug("Filtered prefix request to %(path)r: %(request)s",
                                         {'path': path, 'request': x}, extra={'spider': spider})
                            self.stats.inc_value('prefix/paths', spider=spider)
                        self.stats.inc_value('prefix/filtered', spider=spider)

    def should_follow(self, request, spider):
        path = urlparse_cached(request).path
        return any(path.startswith(p) for p in self.allowed_paths)

    def get_allowed_paths(self, spider):
        """Override this method to implement a different path policy"""
        return getattr(spider, 'allowed_paths', ['/']) # allow all paths by default

    def spider_opened(self, spider):
        self.allowed_paths = self.get_allowed_paths(spider)
        self.external_path_max_depth = getattr(spider, 'external_path_max_depth', 0)
        self.paths_seen = set()


class OffsiteMiddleware(object):
    """
    Depth-aware offsite middleware. Based on from scrapy.spidermiddlewares.offsite.OffsiteMiddleware

    On each spider, set `allowed_domains` to a list of domains.  By default, all domains are allowed.

    On each spider, set `external_domain_max_depth` to a positive integer to
    enable crawling other domains to a limited depth. Defaults to zero.
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
            if not isinstance(x, Request):
                yield x
            else:
                # we have a request
                if x.dont_filter or self.should_follow(x, spider):
                    # domain is explictly allowed, reset depth to zero
                    x.meta['domain_depth'] = 0
                    yield x
                else:
                    depth = x.meta['domain_depth']
                    if depth < self.external_domain_max_depth:
                        # an external domain with less than max depth; record stats & yield request
                        self.stats.inc_value('request_depth_count/%s' % depth, spider=spider)
                        self.stats.max_value('request_depth_max', depth, spider=spider)
                        yield x
                    else:
                        # external domain crawled deeper than max depth; record stats & drop
                        domain = urlparse_cached(x).hostname
                        if domain not in self.domains_seen:
                            self.domains_seen.add(domain)
                            logger.debug("Filtered offsite request to %(domain)r: %(request)s",
                                         {'domain': domain, 'request': x}, extra={'spider': spider})
                            self.stats.inc_value('offsite/domains', spider=spider)
                        self.stats.inc_value('offsite/filtered', spider=spider)

    def should_follow(self, request, spider):
        regex = self.host_regex
        # hostname can be None for wrong urls (like javascript links)
        host = urlparse_cached(request).hostname or ''
        return bool(regex.search(host))

    def get_host_regex(self, spider):
        """Override this method to implement a different offsite policy"""
        allowed_domains = getattr(spider, 'allowed_domains', None)
        if not allowed_domains:
            return re.compile('') # allow all by default
        regex = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in allowed_domains if d is not None)
        return re.compile(regex)

    def spider_opened(self, spider):
        self.host_regex = self.get_host_regex(spider)
        self.external_domain_max_depth = getattr(spider, 'external_domain_max_depth', 0)
        self.domains_seen = set()