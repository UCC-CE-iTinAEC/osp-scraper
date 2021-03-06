import os.path
import re
import uuid

import scrapy.http
from scrapy.utils.httpobj import urlparse_cached

from ..filters import make_filters
from ..items import PageItem
from ..utils import guess_extension

# file types we download
ALLOWED_FILE_TYPES = frozenset({'pdf', 'doc', 'docx', 'rtf'})


class OSPSpider(scrapy.spiders.Spider):
    """Common base class for all syllascrape spiders"""

    # Configure item pipelines
    # See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
    custom_settings = {
        'ITEM_PIPELINES': {
            "osp_scraper.pipelines.WarcFilesPipeline": 300,
            "osp_scraper.pipelines.WarcStorePipeline": 301
        }
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.run_id = str(uuid.uuid1())
        return spider

    def get_parameters(self):
        """return dict of parameters for current spider run"""
        # default values should match various middlewares
        return {
            'filters': [f.asdict() for f in getattr(self, 'filters', [])],
            'start_urls': getattr(self, 'start_urls', []),
            'allowed_file_types': list(getattr(self, 'allowed_file_types', set()))
        }


class FilterSpider(OSPSpider):
    """Filtering spider.

    Parameters
    ==========
    * `start_urls`: a list of initial URLs
    * `allowed_file_types`: a set of binary file extensions to download
    * `filters`: a list of `Filter` objects

    Internals
    =========

    Scrapy's `meta` dictionary is used internally to pass extra metadata
    between pages so it can be added to the final PageItem (`source_url` &
    `source_anchor` are implemented this way).

    The `meta` dictionary is also used for depth tracking - the `depth` item
    keeps track of the depth of the crawl. Depths are checked / reset by the
    spider & downloader middlewares for Filters with infinite depth.

    Attributes
    ==========
    :ivar str run_id: a unique ID for each spider run
    """

    name = "osp_scraper_spider"

    custom_settings = {
        **OSPSpider.custom_settings,
        # Set download timeout to 1 minute (scrapy default is 3 minutes), which
        # is more appropriate for broad crawls.
        'DOWNLOAD_TIMEOUT': 60,
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.allowed_file_types = ALLOWED_FILE_TYPES
        spider.filters = make_filters(
            getattr(cls, 'start_urls', [])
            + kwargs.get('start_urls', [])
            + kwargs.get('database_urls', []),
            max_hops_from_seed=kwargs.get('max_hops_from_seed', 2000)
        )
        return spider

    def parse(self, response):
        # we may end up with a binary response here (instead of in `file_urls`) if
        # we are redirected from a `/plain` URL to a binary blob like `/plain.pdf`
        if isinstance(response, scrapy.http.TextResponse):
            return self.parse_text(response)
        else:
            return self.parse_binary(response)

    def parse_binary(self, response):
        """handler for binary responses"""
        mimetype = response.headers.get('content-type').decode('ascii')
        ext = os.path.splitext(urlparse_cached(response).path)[-1][1:].lower()
        if not ext:
            ext = guess_extension(mimetype).lower()

        if ext in self.allowed_file_types:
            yield PageItem(
                url=response.url,
                content=response.body,
                headers=response.headers,
                status=response.status,
                source_url=response.meta.get('source_url'),
                source_anchor=response.meta.get('source_anchor'),
            )

    def parse_text(self, response):
        """handler for text-based responses"""
        file_urls = []

        for url, anchor in self.extract_links(response):
            meta = {
                'source_url': response.url,
                'source_anchor': anchor,
            }

            # if path ends with a known binary file extension download it, otherwise crawl it
            if os.path.splitext(url)[-1][1:].lower() in self.allowed_file_types:
                file_urls.append((url, meta))
            else:
                yield scrapy.Request(url, meta=meta)

        yield PageItem(
            url=response.url,
            content=response.body,
            headers=response.headers,
            status=response.status,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
            file_urls = file_urls,
        )

    def extract_links(self, response):
        """Generate (url, source_anchor) tuples extracted from the page"""

        for link in response.css('a'):
            # extract the href & urljoin it to the current response
            url = response.urljoin(link.xpath('@href').extract_first())

            # Only follow http(s) URLs (i.e., no `javascript:` or `mailto:`).
            if url.startswith('http'):
                # merge text content of all child nodes of the link
                anchor = " ".join(s.strip() for s in link.css('*::text').extract() if s.strip())

                yield (url, anchor)

        for frame in (response.css("frame") + response.css("iframe")):
            relative_url = frame.css("::attr(src)").extract_first()
            url = response.urljoin(relative_url)

            if url.startswith("http"):
                anchor = frame.css("::attr(name)").extract_first()

                yield (url, anchor)
