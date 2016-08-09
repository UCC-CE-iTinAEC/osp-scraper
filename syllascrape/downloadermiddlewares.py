"""
Offsite Spider Middleware

See documentation in docs/topics/spider-middleware.rst
"""

import re
import logging

from scrapy.http import Request
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.httpobj import urlparse_cached

logger = logging.getLogger(__name__)

class OffsiteMiddleware(object):
    """Middleware to enforce a spider's `allowed_domains` at the downloading layer.

    This is needed because WebFilesPipeline ignores the OffsiteMiddleware for spidering layer.
    """

    def __init__(self, stats):
        self.stats = stats
        self.domains_seen = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_request(self, request, spider):
        # stuff the compiled regex on the spider
        try:
            host_regex = spider._offsite_regex
        except AttributeError:
            host_regex = spider._offsite_regex = self.get_host_regex(spider)

        # some requests for files come from scrapy itself (robots.txt, etc.)
        if 'domain_depth' not in request.meta:
            return

        if request.dont_filter or self.should_follow(request, spider):
            # domain is explicitly allowed, reset depth to zero
            request.meta['domain_depth'] = 0
            return
        else:
            depth = request.meta['domain_depth']
            if depth < self.get_max_depth(spider):
                # an external domain with less than max depth; record stats
                self.stats.inc_value('request_depth_count/%s' % depth, spider=spider)
                self.stats.max_value('request_depth_max', depth, spider=spider)
                return
            else:
                # external domain crawled deeper than max depth; record stats & drop
                domain = urlparse_cached(request).hostname
                if domain and domain not in self.domains_seen:
                    self.domains_seen.add(domain)
                    logger.debug("Filtered offsite request to %(domain)r: %(request)s",
                                 {'domain': domain, 'request': request}, extra={'spider': spider})
                    self.stats.inc_value('offsite/domains', spider=spider)
                self.stats.inc_value('offsite/filtered', spider=spider)

                raise IgnoreRequest

    def should_follow(self, request, spider):
        regex = spider._offsite_regex
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


    def get_max_depth(self, spider):
        """Get the maximum depth allowed for crawling external paths"""
        return getattr(spider, 'external_domain_max_depth', 0)


class PrefixMiddleware(object):
    """Middleware to enforce a spider's `allowed_paths` at the downloading layer.

    This is needed because WebFilesPipeline ignores the PrefixMiddleware for spidering layer.

    See `syllascrape.spidermiddlewares.PrefixMiddleware` for use.
    """
    def __init__(self, stats):
        self.stats = stats
        self.paths_seen = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_request(self, request, spider):
        # some requests for files come from scrapy itself (robots.txt, etc.)
        if 'path_depth' not in request.meta:
            return

        if request.dont_filter or self.should_follow(request, spider):
            # path is explicitly allowed, reset depth to zero
            request.meta['path_depth'] = 0
            return
        else:
            depth = request.meta['path_depth']
            if depth < self.get_max_depth(spider):
                # an external path with less than max depth; record stats
                self.stats.inc_value('request_depth_count/%s' % depth, spider=spider)
                self.stats.max_value('request_depth_max', depth, spider=spider)
                return
            else:
                # external path crawled deeper than max depth; record stats & drop
                path = urlparse_cached(request).path
                if path not in self.paths_seen:
                    self.paths_seen.add(path)
                    logger.debug("Filtered prefix request to %(path)r: %(request)s",
                                 {'path': path, 'request': request}, extra={'spider': spider})
                    self.stats.inc_value('prefix/paths', spider=spider)
                self.stats.inc_value('prefix/filtered', spider=spider)

                raise IgnoreRequest

    def should_follow(self, request, spider):
        path = urlparse_cached(request).path
        return any(path.startswith(p) for p in self.get_allowed_paths(spider))

    def get_allowed_paths(self, spider):
        """Override this method to implement a different path policy"""
        return getattr(spider, 'allowed_paths', ['/']) # allow all paths by default

    def get_max_depth(self, spider):
        """Get the maximum depth allowed for crawling external paths"""
        return getattr(spider, 'external_path_max_depth', 0)