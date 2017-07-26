#!/usr/bin/env python3

import csv

import click

from osp_scraper.utils import extract_urls

@click.command()
@click.argument('old_csv_file', type=click.Path(exists=True))
@click.argument('new_csv_file', type=click.Path(exists=True))
@click.argument('out_csv', type=click.File('w'))
def main(old_csv_file, new_csv_file, out_csv):
    """
    Takes in an old edu csv file and a new edu csv, finds the URLs and custom
    scrapers present in the new file but not the old one, and outputs a csv file
    that contains them.
    """
    with open(old_csv_file) as old_csv, open(new_csv_file) as new_csv:
        old_rows = {row['name']: row for row in csv.DictReader(old_csv)}

        new_reader = csv.DictReader(new_csv)
        writer = csv.DictWriter(out_csv, fieldnames=new_reader.fieldnames)
        writer.writeheader()
        for new_row in new_reader:
            diff_row = dict(new_row)
            old_row = old_rows.get(new_row['name'])

            if old_row:
                old_urls = set(
                    extract_urls(old_row['Database URLs'])
                    + extract_urls(old_row['Doc URLs'])
                    + extract_urls(old_row['Mixed URLs'])
                )

                # NOTE: Currently, the only custom scrapers that use the
                # database urls are campusconcourse and
                # campusconcourse_with_files, so we always include database urls
                # for those rows.  In the future, other custom scrapers might
                # also need database urls.
                if "campusconcourse" not in new_row['Custom Scraper Name']:
                    new_database_urls = extract_urls(new_row['Database URLs'])
                    diff_row['Database URLs'] = ",".join(set(new_database_urls) - old_urls)

                new_doc_urls = extract_urls(new_row['Doc URLs'])
                diff_row['Doc URLs'] = ",".join(set(new_doc_urls) - old_urls)

                new_mixed_urls = extract_urls(new_row['Mixed URLs'])
                diff_row['Mixed URLs'] = ",".join(set(new_mixed_urls) - old_urls)

            if (diff_row['Custom Scraper Name']
                    or diff_row['Database URLs']
                    or diff_row['Doc URLs']
                    or diff_row['Mixed URLs']):
                writer.writerow(diff_row)

if __name__ == '__main__':
    main()
