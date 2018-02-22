#!/usr/bin/env python3

import csv
import logging

import click

from osp_scraper.tasks import get_crawl_job, LocalQueue
from osp_scraper.utils import extract_urls

log = logging.getLogger('edu_repo_crawler')


@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--local', default=False, is_flag=True, help='Run one spider locally instead of queueing it')
@click.option('--institution', default=None, help='Only run spiders for the institution with this ID')
def main(csv_file, local, institution):
    crawl_func = LocalQueue.enqueue if local else get_crawl_job("168h")

    with open(csv_file) as f:
        for row in csv.DictReader(f):
            if not institution or institution == row['id']:
                job = None
                if row['Custom Scraper Name']:
                    # Create a parameter of database URLs that can be used by
                    # custom scrapers as needed.
                    params = {
                        "database_urls": extract_urls(row['Database URLs'])
                    }
                    for scraper_name in row['Custom Scraper Name'].split(","):
                        job = crawl_func(
                            scraper_name.strip(),
                            depends_on=job,
                            **params
                        )

                # Find comma-separated URLs in these columns.
                urls = extract_urls(row['Doc URLs'])
                urls.extend(extract_urls(row['Mixed URLs']))
                if not row['Custom Scraper Name']:
                    urls.extend(extract_urls(row['Database URLs']))

                if urls:
                    log.info("Found %d URLs for %s", len(urls), row['name'])
                    params = {
                        'start_urls': urls
                    }
                    log.debug("Params: %r", params)

                    crawl_func('osp_scraper_spider', depends_on=job, **params)
                else:
                    log.debug("No URLs found for %s", row['name'])

                if institution:
                    break
    if local:
        LocalQueue.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
