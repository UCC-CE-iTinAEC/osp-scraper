#!/usr/bin/env python3

import sys
import os.path
import csv
import logging
from logging.config import dictConfig
import re
from urllib.parse import urlparse

from syllascrape.spiders import Spider
from syllascrape.spiders import url_to_prefix_params
from syllascrape.filterware import Filter

from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'scrapy': {
            'level': 'INFO',
        },
        'twisted': {
            'level': 'ERROR',
        },
    }
}

dictConfig(LOGGING)

def make_params(url):
    u = urlparse(url)

    hostname = re.escape(u.hostname) if u.hostname is not None else None
    port = re.escape(u.port) if u.port is not None else None

    return {
        'start_urls': [url],
        'allowed_file_types': {'pdf', 'doc', 'docx'},
        'filters': [
            # allow paths starting with prefix, with matching hostname & port
            Filter.compile('allow', pattern='regex',
                           hostname=hostname,
                           port=port,
                           path=re.escape(u.path if u.path.endswith('/') else
                                          os.path.dirname(u.path) + '/') + '.*',
                           ),
            # allow other paths to a depth of 2
            Filter.compile('allow', pattern='regex',
                           max_depth=2, hostname=hostname, port=port),
            # allow other hosts to a depth of 1
            Filter.compile('allow', pattern='regex', max_depth=1)
        ],
    }


def main(csv_file):
    with open(csv_file) as f:
        row = next(csv.reader(f))

    kwargs = make_params(row[0])
    print(kwargs)

    process = CrawlerProcess(get_project_settings())
    process.crawl(Spider, **kwargs)
    process.start()


def usage():
    print("%s <csv_file>" % os.path.basename(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    else:
        main(sys.argv[1])