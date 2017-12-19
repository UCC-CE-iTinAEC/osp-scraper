import logging

from scrapy import Request

from .items import PageItem
from .filterware import check_filters

logger = logging.getLogger(__name__)


class DepthMiddleware(object):
    """Middleware to set depths and hops_from_seed

    This middleware handles all logic for setting depth and
    hops_from_seeds on requests and items.
    """

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_spider_output(self, response, result, spider):
        depth = response.meta.get('depth', 0)
        hops_from_seed = response.meta.get('hops_from_seed', 0)

        for obj in result:
            if isinstance(obj, PageItem):
                obj['depth'] = depth
                obj['hops_from_seed'] = hops_from_seed

                for url, meta in obj['file_urls']:
                    meta['depth'] = depth + 1
                    meta['hops_from_seed'] = hops_from_seed + 1

            elif isinstance(obj, Request):
                obj.meta['depth'] = depth + 1
                obj.meta['hops_from_seed'] = hops_from_seed + 1

            yield obj
