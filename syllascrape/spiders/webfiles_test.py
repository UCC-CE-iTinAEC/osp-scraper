"""A spider for testing WebStorePipeline
"""

import scrapy
import os.path

from . import Spider
from ..items import PageItem

class WebFilesTestSpider(Spider):
    name = "webfiles_test"
    allowed_domains = ["wearpants.org"]

    allowed_paths = [
        "/bogus/",
        "/blog/",
        "/petecode/",
        "/documents/",
    ]

    start_urls = [
        "http://wearpants.org/",
    ]
