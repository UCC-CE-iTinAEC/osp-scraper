# -*- coding: utf-8 -*-

from . import BaseSpider, ALLOWED_FILE_TYPES
from ..filterware import Filter
from ..items import PageItem

class CustomSpider(BaseSpider):
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.allowed_file_types = ALLOWED_FILE_TYPES
        spider.filters = [Filter.compile('allow')]
        return spider

    def start_requests(self):
        """
        Override in subclass for each site when necessary.  Overriding
        start_requests is not necessary when implementing parse.

        By default, sets both the 'depth' and 'hops_from_seed' meta content to
        0.  This can be useful when making calls to parse_for_files directly out
        of parse.
        """
        for request in super().start_requests():
            request.meta['depth'] = 0
            request.meta['hops_from_seed'] = 0
            yield request

    def parse(self, response):
        """
        Implement in subclass for each site when necessary.  Implementing parse
        is not necessary when implementing start_requests.
        """
        raise NotImplementedError

    def extract_links(self, response):
        """
        Generate (url, source_anchor) tuples extracted from the page

        Implement in subclass for each site.
        """
        return
        yield

    def parse_for_files(self, response):
        """
        Generate PageItems with all necessary metadata and with
        file_urls created from tuples generated by extract_links

        If you set the require_files flag on response.meta to True, a PageItem
        will only be yielded if extract_links yields at least one file.
        """
        file_urls = []

        for url, anchor in self.extract_links(response):
            meta = {
                'source_url': response.url,
                'source_anchor': self.clean_whitespace(anchor),
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
            }

            file_urls.append((response.urljoin(url), meta))

        if response.meta.get('require_files') and not file_urls:
            # No files found so don't yield PageItem
            return

        yield PageItem(
            url=response.url,
            content=response.body,
            headers=response.headers,
            status=response.status,
            source_url=response.meta['source_url'],
            source_anchor=self.clean_whitespace(response.meta['source_anchor']),
            depth=response.meta['depth'],
            hops_from_seed=response.meta['hops_from_seed'],
            file_urls=file_urls
        )

    def clean_whitespace(self, s):
        """
        Condenses all consecutive whitespace in a string to a single
        space and removes leading and trailing whitespace.
        """
        return " ".join(s.split())
