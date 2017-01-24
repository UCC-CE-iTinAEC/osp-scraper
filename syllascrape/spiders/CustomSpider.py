# -*- coding: utf-8 -*-

import re
import uuid

from scrapy.spiders import Spider

from ..filterware import Filter
from ..items import PageItem 

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

    def get_file_links(self, response):
        return
        yield

    def parse_for_files(self, response):
        file_urls = []

        for url, anchor in self.get_file_links(response):
            meta={
                'source_url': response.url,
                'source_anchor': anchor,
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
            }

            file_urls.append((url, meta))

        yield PageItem(
            url=response.url,
            content=response.body,
            headers=response.headers,
            status=response.status,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
            depth=response.meta.get('depth'),
            hops_from_seed=response.meta.get('hops_from_seed'),
            file_urls=file_urls
        )

    def clean_whitespace(self, s):
        return re.sub(r"\s+", " ", s).strip()

