#!/usr/bin/env python3

from collections import defaultdict
import logging
from urllib.parse import urlparse

import click

from osp_scraper.tasks import get_crawl_job


log = logging.getLogger('seed_url_crawler')


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--timeout', default="24h", help="Maximum runtime of the jobs")
def main(path, timeout):
    """Starts spiders for individual URLs in a text file.

    Takes one input file, which should contain a URL on each line.
    This script groups the URLs by domain and queues a spider job
    for each domain.
    """
    groups = defaultdict(list)
    for url in open(path):
        domain = urlparse(url.strip()).netloc
        groups[domain].append(url.strip())

    queue_crawl = get_crawl_job(timeout=timeout)
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
