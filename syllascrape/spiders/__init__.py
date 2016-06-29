import scrapy.spiders
import scrapy.http
from scrapy.utils.httpobj import urlparse_cached

import os.path

from ..items import PageItem
from ..utils import guess_extension

class Spider(scrapy.spiders.Spider):
    """Base class for syllascrape spiders.

    Subclassers must override the `parse_text` method to implement a crawling strategy

    :cvar int version: a version number for the spider. This should be incremented by the developer for each version of code deployed to production
    """

    @property
    def version_string(self):
        """return the name/version"""
        return "%s/%d" % (self.name, self.version)

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
        raise NotImplementedError