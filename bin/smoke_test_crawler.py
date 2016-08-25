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

def make_params():
    hostname = re.escape('wearpants.org')

    return {
        'start_urls': ['https://wearpants.org/'],
        'allowed_file_types': {'pdf', 'doc', 'docx'},
        'filters': [
            Filter.compile('deny', pattern='regex',
                           source_anchor='contact',
                           ),

            Filter.compile('allow', pattern='regex',
                           hostname=hostname,
                           path=re.escape('/') + '.*',
                           ),
        ],
    }


def main():

    kwargs = make_params()

    process = CrawlerProcess(get_project_settings())
    process.crawl(Spider, **kwargs)
    process.start()

if __name__ == '__main__':
    main()