# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from pprint import pformat

class BaseItem(scrapy.Item):
    url = scrapy.Field()
    domain = scrapy.Field()
    source_url = scrapy.Field()
    source_anchor = scrapy.Field() # anchor text on source page
    retrieved = scrapy.Field() # integer seconds since epoch
    spider = scrapy.Field() # spider.name/1.0
    checksum = scrapy.Field() # MD5 sum of content
    length = scrapy.Field() # length of content
    mimetype = scrapy.Field() # Content-Type header from response

# we have slightly different items for `pages` (which contain raw content in memory)
# and `files` (where bytes have be saved to storage already by scrapy). These items
# are internal to scrapy only; the final format written will look like FileItem
# see http://doc.scrapy.org/en/latest/topics/media-pipeline.html

class PageItem(BaseItem):
    content = scrapy.Field() # raw bytes
    file_urls = scrapy.Field() # for use with WebFilesPipeline - list of 2-tuples of (url, meta dict)
    files = scrapy.Field() # gets results of WebFilesPipeleine

    def get_metadata(self):
        """return a dict containing only metadata (dropping `content`, etc.)."""
        return {k:v for k, v in self.items() if k not in ('content', 'file_urls', 'files')}

    # custom repr so we don't show the entire page when logging
    def __repr__(self):
        return pformat(self.get_metadata())

class FileItem(BaseItem):
    pass