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

        file_urls = [x for x in ((r.xpath('@src').extract_first(), {'source_anchor': r.xpath('@alt').extract_first()})
                                 for r in response.css('img'))
                     if x[0] is not None
                    ]

        for link in response.css('a'):
            # extract the href & urljoin it to the current response
            url = response.urljoin(link.xpath('@href').extract_first())

            # merge text content of all child nodes of the link
            anchor = " ".join(s.strip() for s in link.css('*::text').extract() if s.strip())

            if os.path.splitext(url)[-1][1:] in self.settings['FILES_EXTENSIONS']:
                file_urls.append((url, {'source_anchor': anchor}))
            else:
                yield scrapy.Request(url, meta={'source_url': response.url,'source_anchor': anchor})

        if file_urls:
            self.logger.info("On page %r got file_urls %r", response.url, file_urls)

        yield PageItem(
            url=response.url,
            content=response.body,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
            file_urls = file_urls
        )

