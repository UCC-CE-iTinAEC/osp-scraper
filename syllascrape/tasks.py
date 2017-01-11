

from __future__ import absolute_import

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from .spiders import Spider


def crawl(spider, *args, **kwargs):
    """Run a spider.

    Args:
        spider (str): The Scrapy `name` of the spider.
    """
    proc = CrawlerProcess(get_project_settings())
    proc.crawl(spider)
    proc.join()
