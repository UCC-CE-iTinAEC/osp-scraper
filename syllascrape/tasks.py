

from __future__ import absolute_import

import re
import urllib.parse
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from rq.decorators import job

from .spiders import Spider
from .filterware import Filter
from .services import redis_conn


# a list of base domains to blacklist; subdomains blocked too
blacklist_domains = [
    'facebook.com',
    'reddit.com',
    'twitter.com',
    'linkedin.com',
    'wikipedia.org',
]

blacklist_re = "^" + "|".join(
    "((.*\.)?%s$)" % re.escape(x)
    for x in blacklist_domains
)


def make_params(seed_urls):
    """Generate parameters for a spider from a list of URLs.

    * Allow paths with matching prefix to infinite depth
    * Allow same hostname to max depth of 2
    * Allow other domains to max depth of 1

    Based on syllascrape.spiders.url_to_prefix_params.

    Args:
        seed_urls (list)
    """
    # parameters for a spider
    d = {
        'start_urls': [],
        'allowed_file_types': {'pdf', 'doc', 'docx'},
        'filters': [],
    }

    # blacklist domains
    d['filters'].append(
        Filter.compile(
            'deny',
            pattern='regex',
            hostname=blacklist_re
        )
    )

    # merge parameters from several seed urls, with unique domains & paths
    for url in seed_urls:
        d['start_urls'].append(url)

        u = urllib.parse.urlparse(url)
        prefix = re.escape(u.path if u.path.endswith('/') else os.path.dirname(u.path) + '/')
        hostname=re.escape(u.hostname) if u.hostname is not None else None
        port=re.escape(str(u.port)) if u.port is not None else None

        # allow prefix to infinite depth
        d['filters'].append(Filter.compile('allow',
            pattern='regex',
            hostname=hostname,
            port=port,
            path=prefix + ".*"
        ))

        # allow same hostname to max depth 2
        d['filters'].append(
            Filter.compile(
                'allow',
                pattern='regex',
                hostname=hostname,
                port=port,
                max_depth=2
            )
        )

    # allow other domains w/ max depth 1
    d['filters'].append(Filter.compile('allow', max_depth=1))

    return d


@job('default', connection=redis_conn, timeout=86400)
def crawl(spider, *args, **kwargs):
    """Run a spider.

    Args:
        spider (str): The Scrapy `name` of the spider.
    """
    proc = CrawlerProcess(get_project_settings())
    proc.crawl(spider, *args, **kwargs)
    proc.start()
