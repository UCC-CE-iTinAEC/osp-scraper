

from __future__ import absolute_import

import re
import urllib.parse
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from rq.decorators import job

from .spiders import FilterSpider
from .filterware import Filter
from .services import redis_conn


# Limit crawls to 1 week.
# TODO: Why doesn't it work to pass this via --worker-ttl to the worker?
@job('default', connection=redis_conn, timeout=604800)
def crawl(spider, *args, **kwargs):
    """Run a spider.

    Args:
        spider (str): The Scrapy `name` of the spider.
    """
    settings = get_project_settings()
    if kwargs.get('ignore_robots_txt') is True:
        settings.attributes.get('ROBOTSTXT_OBEY').value = False

    proc = CrawlerProcess(settings)
    proc.crawl(spider, *args, **kwargs)
    proc.start()
