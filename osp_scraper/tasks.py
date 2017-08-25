

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

# Run crawls for 1 day max.
@job('default', connection=redis_conn, timeout=86400)
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

def get_crawl_job(timeout='24h'):
    """Returns a function that will add a crawl call to the Redis queue

    Args:
        timeout (int/string): the maximum runtime of the job
    """
    return job('default', connection=redis_conn, timeout=timeout)(crawl).delay
