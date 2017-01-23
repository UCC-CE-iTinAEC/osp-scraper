# -*- coding: utf-8 -*-

import re
import uuid

from scrapy.spiders import Spider

from ..filterware import Filter

class CustomSpider(Spider):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.run_id = str(uuid.uuid1())
        spider.allowed_file_types = {'pdf', 'doc', 'docx'}
        spider.filters = [Filter.compile('allow')]
        return spider

    def get_parameters(self):
        """return dict of parameters for current spider run"""
        # default values should match various middlewares
        return {
            'filters': [f.asdict() for f in getattr(self, 'filters', [])],
            'start_urls': getattr(self, 'start_urls', []),
            'allowed_file_types': list(getattr(self, 'allowed_file_types', set()))
        }
