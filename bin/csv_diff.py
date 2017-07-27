#!/usr/bin/env python3

import csv

import click

def extract_urls(s):
    """return a list of clean URLs from a comma-separated string"""
    urls = (u.strip() for u in s.split(','))
    urls = (u for u in urls if u.startswith('http'))
    return list(urls)

@click.command()
@click.argument('old_csv_file', type=click.Path(exists=True))
@click.argument('new_csv_file', type=click.Path(exists=True))
@click.argument('out_csv', type=click.File('w'))
@click.option(
    '--diff_custom_scrapers', default=False, is_flag=True,
    help=("Consider custom scrapers as part of the diff.  Without this flag, "
          "rows containing 'Custom Scraper Name's are always included in "
          "OUT_CSV."))
def main(old_csv_file, new_csv_file, out_csv, diff_custom_scrapers):
    """
    Takes in an old edu csv file and a new edu csv, finds the URLs and custom
    scrapers present in the new file but not the old one, and outputs a csv file
    that contains them.

    Rows are compared based on the value in the 'id' column.  In order for the
    diff to work properly, ensure that each row has a unique 'id' value
    associated with it.
    """
    with open(old_csv_file) as old_csv, open(new_csv_file) as new_csv:
        old_rows = {row['id']: row for row in csv.DictReader(old_csv)}

        new_reader = csv.DictReader(new_csv)
        writer = csv.DictWriter(out_csv, fieldnames=new_reader.fieldnames)
        writer.writeheader()
        for new_row in new_reader:
            diff_row = dict(new_row)
            old_row = old_rows.get(new_row['id'])

            if old_row:
                old_urls = set(
                    extract_urls(old_row['Database URLs'])
                    + extract_urls(old_row['Doc URLs'])
                    + extract_urls(old_row['Mixed URLs'])
                )

                if diff_custom_scrapers:
                    if new_row['Custom Scraper Name'] == old_row['Custom Scraper Name']:
                        diff_row['Custom Scraper Name'] = ""

                # Always include un-diffed 'Database URLs' for rows that have a
                # custom scraper in case those 'Database URLs' are used by that
                # scraper.
                if not diff_row['Custom Scraper Name']:
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
