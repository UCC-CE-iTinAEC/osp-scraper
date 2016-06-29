"""A spider for testing WebStorePipeline
"""

import scrapy
from . import Spider

from ..items import PageItem

class WebStoreTestSpider(Spider):
    name = "webstore_test"
    version = 1
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/",
    ]

    def parse(self, response):
        yield PageItem(
            url=response.url,
            content=response.body,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
        )

        for link in response.css('div.cat-item a'):
            # extract the href & urljoin it to the current response
            url = response.urljoin(link.xpath('@href').extract_first())

            # merge text content of all child nodes of the link
            anchor = " ".join(s.strip() for s in link.css('*::text').extract() if s.strip())

            yield scrapy.Request(url, meta={'source_url': response.url,'source_anchor': anchor})
