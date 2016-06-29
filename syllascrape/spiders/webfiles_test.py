"""A spider for testing WebStorePipeline
"""

import scrapy

import os.path

from . import Spider
from ..items import PageItem

class WebFilesTestSpider(Spider):
    name = "webfiles_test"
    version = 1
    allowed_domains = ["wearpants.org"]
    start_urls = [
        "http://wearpants.org/",
    ]

    def parse(self, response):

        file_urls = []
        for r in response.css('img'):
            src = r.xpath('@src').extract_first()
            if src is not None:
                alt = r.xpath('@alt').extract_first() or ''
                file_urls.append((src, {'source_anchor': alt}))

        for link in response.css('a'):
            # extract the href & urljoin it to the current response
            url = response.urljoin(link.xpath('@href').extract_first())

            # merge text content of all child nodes of the link
            anchor = " ".join(s.strip() for s in link.css('*::text').extract() if s.strip())

            if os.path.splitext(url)[-1][1:].lower() in self.settings['FILES_EXTENSIONS']:
                file_urls.append((url, {'source_anchor': anchor}))
            else:
                yield scrapy.Request(url, meta={'source_url': response.url,'source_anchor': anchor})

        yield PageItem(
            url=response.url,
            content=response.body,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
            mimetype = response.headers.get('content-type').decode('ascii'),
            file_urls = file_urls
        )

