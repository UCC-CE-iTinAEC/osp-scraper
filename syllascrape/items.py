# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from pprint import pformat

class PageItem(scrapy.Item):
    url = scrapy.Field()
    source_url = scrapy.Field()
    source_anchor = scrapy.Field() # anchor text on source page
    retrieved = scrapy.Field() # integer seconds since epoch
    spider_name = scrapy.Field() # spider name
    spider_revision = scrapy.Field() # git revision number of source code
    spider_parameters = scrapy.Field() # dict of spider parameters
    spider_run_id = scrapy.Field() # string UUID to identify this run
    length = scrapy.Field() # length of content
    depth = scrapy.Field() # crawl depth - reset by filters
    hops_from_seed = scrapy.Field() # how many hops from start URL

    content = scrapy.Field() # raw bytes
    headers = scrapy.Field() # scrapy Headers object
    status = scrapy.Field() # HTTP status code
    file_urls = scrapy.Field() # for use with WebFilesPipeline - list of 2-tuples of (url, meta dict)
    files = scrapy.Field() # gets results of WebFilesPipeleine

    def get_metadata(self):
        """return a dict containing only metadata (dropping `content`, etc.)."""
        return {k:v for k, v in self.items() if k not in ('content', 'file_urls', 'files', 'headers', 'status')}

    # custom repr so we don't show the entire page when logging
    def __repr__(self):
        return pformat(self.get_metadata())