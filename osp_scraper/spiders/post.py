# -*- coding: utf-8 -*-

import scrapy

from ..spiders import FilterSpider

class PostSpider(FilterSpider):
    """
    This spider can submit the given URLs as x-www-form-urlencoded POST
    requests, and then continues as a general crawl. This avoids having to
    create custom mapping spiders for many different sites.
    """
    name = "post"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        kwargs['start_urls'] = kwargs['database_urls']
        spider = super().from_crawler(crawler, *args, **kwargs)
        return spider

    def start_requests(self):
        for start_url in self.database_urls:
            url, body = start_url.split("?POST_BODY=", 1)
            yield scrapy.FormRequest(
                url,
                method="POST",
                headers={
                    'Content-Type': "application/x-www-form-urlencoded"
                },
                body=body,
                meta={
                    'source_url': url,
                    'source_anchor': body
                },
                callback=self.parse
            )
