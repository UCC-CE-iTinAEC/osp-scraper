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

# a list of base domains to blacklist; subdomains blocked too
blacklist_domains = ['facebook.com', 'reddit.com', 'twitter.com', 'linkedin.com', 'wikipedia.org']
blacklist_re = "^" + "|".join("((.*\.)?%s$)" % re.escape(x) for x in blacklist_domains)

def make_params(seed_urls):
    """Generate parameters for a spider from a list of URLs

    * Allow paths with matching prefix to infinite depth
    * Allow same hostname to max depth of 2
    * Allow other domains to max depth of 1

    based on syllascrape.spiders.url_to_prefix_params
    """
    # parameters for a spider
    d = {
        'start_urls': [],
        'allowed_file_types': {'pdf', 'doc', 'docx'},
        'filters': [],
        }

    # blacklist domains
    d['filters'].append(Filter.compile('deny',
                                       pattern='regex',
                                       hostname=blacklist_re
                                       ))

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
        d['filters'].append(Filter.compile('allow',
                                           pattern='regex',
                                           hostname=hostname,
                                           port=port,
                                           max_depth=2
                                           ))

    # allow other domains w/ max depth 1
    d['filters'].append(Filter.compile('allow', max_depth=1))

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
                params = make_params(urls)
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
