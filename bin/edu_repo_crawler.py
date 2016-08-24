#!/usr/bin/env python3

import sys
import os.path
import csv
import logging
import itertools
import urllib.parse
import re

import syllascrape.tasks
from syllascrape.filterware import Filter

log = logging.getLogger('edu_repo_crawler')

def make_prefix_params(seed_urls):
    """Generate parameters for a prefix spider from a list of URLs

    based on from syllascrape.spiders.url_to_prefix_params
    """
    # parameters for a spider
    d = {
        'start_urls': [],
        'allowed_file_types': {'pdf', 'doc', 'docx'},
        'filters': [],
        }

    # merge parameters from several seed urls, with unique domains & paths
    for url in seed_urls:
        u = urllib.parse.urlparse(url)
        d['start_urls'].append(url)

        path = u.path if u.path.endswith('/') else os.path.dirname(u.path) + '/'

        d['filters'].append(Filter.compile(
            pattern='regex',
            hostname=re.escape(u.hostname),
            port=re.escape(u.port),
            path=re.escape(path) + ".*"
        ))
    return d

def extract_urls(s):
    """return a list of clean URLs from a comma-separated string"""
    urls = (u.strip() for u in s.split(','))
    urls = (u for u in urls if u.startswith('http'))
    return list(urls)

def main(csv_file):
    with open(csv_file) as f:
        for row in csv.DictReader(f):
            # find comma-separated URLs in these columns
            urls = extract_urls(row['Doc URLs'])
            urls.extend(extract_urls(row['Mixed URLs']))
            urls.extend(extract_urls(row['Database URLs']))

            if urls:
                log.info("Found %d URLs for %s", len(urls), row['biz_name'])
                params = make_prefix_params(urls)
                log.debug("Parameters: %r", params)
                syllascrape.tasks.crawl.delay(**params)
            else:
                log.debug("No URLs found for %s", row['biz_name'])

def usage():
    print("%s <csv_file>" % os.path.basename(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    else:
        logging.basicConfig(level=logging.INFO)
        main(sys.argv[1])
