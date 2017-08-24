#!/usr/bin/env python3

from collections import defaultdict
import logging
from urllib.parse import urlparse

import click

from osp_scraper.tasks import get_crawl_job


log = logging.getLogger('seed_url_crawler')


@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    groups = defaultdict(list)
    for url in open(path):
        domain = urlparse(url.strip()).netloc
        groups[domain].append(url.strip())

    queue_crawl = get_crawl_job(timeout='24h')
    for domain, urls in groups.items():
        queue_crawl(
            'osp_scraper_spider',
            start_urls=urls,
            ignore_robots_txt=True
        )

        log.info(f'{len(urls)} URLs for {domain}')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
