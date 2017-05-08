#!/usr/bin/env python3

import logging

import click

from osp_scraper.tasks import make_params, crawl

log = logging.getLogger('edu_repo_crawler')

@click.command()
@click.argument('url')
def main(url):
    params = make_params([url])
    log.debug("Parameters: %r", params)

    crawl('osp_scraper_spider', **params)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
