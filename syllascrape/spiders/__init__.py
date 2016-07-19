import scrapy.spiders
import scrapy.http
from scrapy.utils.httpobj import urlparse_cached

from urllib.parse import urlparse
import os.path

from ..items import PageItem
from ..utils import guess_extension
from .. import version

class Spider(scrapy.spiders.Spider):
    """Base class for syllascrape spiders.

    Subclassers must override the `parse_text` method to implement a crawling strategy

    :cvar int version: a version number for the spider. This should be incremented by the developer for each version of code deployed to production
    """

    name = "syllascrape_spider"

    def get_parameters(self):
        """return dict of parameters for current spider run"""
        # default values should match various middlewares
        return {
            'allowed_domains': getattr(self, 'allowed_domains', ['']),
            'allowed_paths': getattr(self, 'allowed_paths', ['/']),
            'start_urls': getattr(self, 'start_urls', []),
        }

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

        if ext in self.settings['FILES_EXTENSIONS']:
            yield PageItem(
                url=response.url,
                content=response.body,
                source_url=response.meta.get('source_url'),
                source_anchor=response.meta.get('source_anchor'),
                mimetype = mimetype,
            )

    def parse_text(self, response):
        """handler for text-based responses"""
        file_urls = []

        for url, anchor in self.extract_links(response):
            # if path ends with a known binary file extension download it, otherwise crawl it
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

    def extract_links(self, response):
        """return a list of (url, source_anchor) tuples extracted from the page"""

        for link in response.css('a'):
            # extract the href & urljoin it to the current response
            url = response.urljoin(link.xpath('@href').extract_first())

            # merge text content of all child nodes of the link
            anchor = " ".join(s.strip() for s in link.css('*::text').extract() if s.strip())

            yield (url, anchor)


def url_to_prefix_params(url):
    """Generate parameters for a prefix spider.

    If the path component ends with a `/` it will be used-as is; otherwise
    the final path component is assumed to be a filename and will be dropped.

    :arg str url: the seed url
    :returns: parameters for :cls:`Spider`: `start_urls`, `allowed_domains`, `allowed_paths`
    :rtype: dict
    """
    u = urlparse(url)

    return {
        'start_urls': [url],
        'allowed_domains': [u.netloc],
        'allowed_paths': [u.path if u.path.endswith('/') else os.path.dirname(u.path) + '/']
    }