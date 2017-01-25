#!/usr/bin/env python3

import sys
import os.path
import csv
import logging
import itertools
import urllib.parse
import re

from syllascrape.tasks import make_params, crawl


log = logging.getLogger('edu_repo_crawler')


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

            if row.get('Custom Scraper Name'):
                crawl.delay(row['Custom Scraper Name'])

            if urls:
                log.info("Found %d URLs for %s", len(urls), row['name'])
                params = make_params(urls)
                log.debug("Parameters: %r", params)

                if row['robots.txt'].lower() == "ignore":
                    params['ignore_robots_txt'] = True
                    log.info("Ignoring robots.txt")
                    
                crawl.delay('syllascrape_spider', **params)
            else:
                log.debug("No URLs found for %s", row['name'])


def usage():
    print("%s <csv_file>" % os.path.basename(sys.argv[0]))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    else:
        logging.basicConfig(level=logging.INFO)
        main(sys.argv[1])
