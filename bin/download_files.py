#!/usr/bin/env python3

import logging

import click

from osp_scraper.tasks import crawl, get_crawl_job

log = logging.getLogger('file_crawler')


@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option(
    '--local',
    default=False,
    is_flag=True,
    help="Run spiders locally instead of queueing them"
)
def main(csv_file, local):
    crawl_func = crawl if local else get_crawl_job("168h")

    crawl_func("file_downloader", csv_file=csv_file)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
