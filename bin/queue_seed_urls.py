#!/usr/bin/env python3

import csv
import logging

import click

from osp_scraper.tasks import crawl
from osp_scraper.utils import extract_urls


log = logging.getLogger('seed_url_crawler')


@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
def main(csv_file):

    with open(csv_file) as fh:
        for row in csv.DictReader(fh):

            urls = (
                extract_urls(row['Doc URLs']) +
                extract_urls(row['Mixed URLs'])
            )

            crawl.delay(
                'osp_scraper_spider',
                start_urls=urls,
                ignore_robots_txt=True,
            )

            log.debug(urls)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
