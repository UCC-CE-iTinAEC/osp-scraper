#!/usr/bin/env python3

import csv

import click

@click.command()
@click.argument('in_csv_file', type=click.File('r'))
@click.argument('out_csv', type=click.File('w'))
@click.argument('scraper_names', nargs=-1)
@click.option(
    '--only_database/--not-only-database', default=True,
    help=("Whether URLs from 'Doc URLs' and 'Mixed URLs' should be present in "
          "the output or not.  Default: Only keep 'Database URLs'."))
def main(in_csv_file, out_csv, scraper_names, only_database):
    """
    Filter an EDU CSV by custom scraper name(s).
    """
    reader = csv.DictReader(in_csv_file)
    writer = csv.DictWriter(out_csv, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        if row['Custom Scraper Name'] in scraper_names:
            if only_database:
                row['Doc URLs'] = ""
                row['Mixed URLs'] = ""

            writer.writerow(row)

if __name__ == '__main__':
    main()
