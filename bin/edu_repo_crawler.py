#!/usr/bin/env python3

import csv
import logging

import click

from osp_scraper.tasks import crawl
from osp_scraper.utils import extract_urls


log = logging.getLogger('edu_repo_crawler')

@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--local', default=False, is_flag=True, help='Run one spider locally instead of queueing it.')
@click.option('--institution', default=None, help='Only run spiders for the institution with this ID.')
def main(csv_file, local, institution):
    """
    Runs crawls based on the information from an EDU-formatted CSV.  For each
    row of the CSV, up to two types of crawls will be generated:

        - Crawls made over URLs in the 'Database URLs', 'Doc URLs' and 'Mixed
          URLs' columns by `osp_scraper_spider`

        - Crawls made by a custom scraper with spider `name` specified in the
          'Custom Scraper Name' column.

    If a row has an entry in the 'Custom Scraper Name' column, any URLs in the
    'Database URLs' column will be fed as an extra parameter to the custom
    scraper and will not be crawled by `osp_scraper_spider`.

    If a row contains the word "ignore" in the `robots.txt` column, the
    robots.txt of any domains being crawled by `osp_scraper_spider` will be
    ignored.
    """
    crawl_func = crawl if local else crawl.delay

    with open(csv_file) as f:
        for row in csv.DictReader(f):
            if not institution or institution == row['id']:
                # Run custom scraper, but only if not running locally.
                if not local and row['Custom Scraper Name']:
                    # Create a parameter of database URLs that can be used by
                    # custom scrapers as needed.
                    params = {
                        "database_urls": extract_urls(row['Database URLs'])
                    }
                    crawl_func(row['Custom Scraper Name'], **params)

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

                    if row['robots.txt'].strip().lower() == "ignore":
                        params['ignore_robots_txt'] = True
                        log.info("Ignoring robots.txt")

                    crawl_func('osp_scraper_spider', **params)
                else:
                    log.debug("No URLs found for %s", row['name'])

                if institution:
                    break

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
