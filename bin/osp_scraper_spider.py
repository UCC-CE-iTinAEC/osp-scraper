#!/usr/bin/env python3

import logging

import click

from osp_scraper.tasks import crawl


@click.command()
@click.argument('url')
def main(url):
    params = {
        'start_urls': [url]
    }

    crawl('osp_scraper_spider', **params)


if __name__ == '__main__':
    main()
