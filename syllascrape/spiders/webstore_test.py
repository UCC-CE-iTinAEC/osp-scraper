"""A spider for testing WebStorePipeline

based on https://github.com/scrapy/dirbot
"""

import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector

from ..items import PageItem

class WebStoreTestSpider(Spider):
    name = "webstore_test"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/",
    ]

    def parse(self, response):
        yield PageItem(content=response.body,
                       source_url=response.meta.get('source_url'),
                       # XXX provenance?
                       )

        for link in response.css('div.cat-item a::attr(href)'):
            yield scrapy.Request(response.urljoin(link.extract()), meta={'source_url': response.url})
