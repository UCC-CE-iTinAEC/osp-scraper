# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseItem(scrapy.Item):
    url = scrapy.Field()
    domain = scrapy.Field()
    source_url = scrapy.Field()
    retrieved = scrapy.Field() # integer seconds since epoch
    spider = scrapy.Field() # spider.name/1.0
    provenance = scrapy.Field() # freetext for description of origin for manual uploads
    checksum = scrapy.Field() # MD5 sum of content
    length = scrapy.Field() # length of content

    # XXX mimetype?

# we have slightly different items for `pages` (which contain raw content in memory)
# and `files` (where bytes have be saved to storage already by scrapy). These items
# are internal to scrapy only; the final format written will look like FileItem
# see http://doc.scrapy.org/en/latest/topics/media-pipeline.html

class PageItem(BaseItem):
    content = scrapy.Field() # raw bytes

class FileItem(BaseItem):
    pass