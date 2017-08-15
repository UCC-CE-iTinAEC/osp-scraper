#!/usr/bin/env python3

import csv
import logging

import click

from osp_scraper.tasks import crawl
from osp_scraper.seeds import SeedURLList


log = logging.getLogger('seed_url_crawler')


@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):

    seeds = SeedURLList.from_file(path)

    groups = seeds.group_by_domain()

    for domain, urls in groups.items():

        crawl.delay(
            'osp_scraper_spider',
            start_urls=urls,
            ignore_robots_txt=True,
        )

        log.info(f'{len(urls)} URLs for {domain}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
