#!/usr/bin/env python3
"""Create a CSV file that's a diff of two CSVs with respect to certain columns."""

import collections
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
def main(old_csv_file, new_csv_file, out_csv):
    with open(old_csv_file) as old_csv, open(new_csv_file) as new_csv:
        old_reader = csv.DictReader(old_csv)
        new_reader = csv.DictReader(new_csv)
        # id_list will contain
        #   1) The 'id's (first CSV column) of the rows that have been changed.
        #   2) Differences between certain columns in the old and new CSVs.
        id_list = collections.defaultdict(dict)

        old_by_id = collections.defaultdict(dict)
        for old_row in old_reader:
            row_id = old_row['id']
            old_by_id[row_id]['Doc URLs'] = old_row.get('Doc URLs','')
            old_by_id[row_id]['Mixed URLs'] = old_row.get('Mixed URLs','')
            old_by_id[row_id]['1st Search Result Page'] = old_row.get('1st Search Result Page', '')
            old_by_id[row_id]['Database URLs'] = old_row.get('Database URLs', '')
            old_by_id[row_id]['Custom Scraper Name'] = old_row.get('Custom Scraper Name', '')

        new_by_id = collections.defaultdict(dict)
        for new_row in new_reader:
            row_id = new_row['id']
            new_by_id[row_id]['Doc URLs'] = new_row.get('Doc URLs','')
            new_by_id[row_id]['Mixed URLs'] = new_row.get('Mixed URLs','')
            new_by_id[row_id]['1st Search Result Page'] = new_row.get('1st Search Result Page', '')
            new_by_id[row_id]['Database URLs'] = new_row.get('Database URLs', '')
            new_by_id[row_id]['Custom Scraper Name'] = new_row.get('Custom Scraper Name', '')

        # TODO: Handle rows that are exclusively in the new_csv_file?
        for new_id, new_item in new_by_id.items():
            new_doc_url_set = set(extract_urls(new_item['Doc URLs']))
            new_mixed_url_set = set(extract_urls(new_item['Mixed URLs']))
            new_search_url_set = set(extract_urls(new_item['1st Search Result Page']))

            scraper_name = new_item.get('Custom Scraper Name', '')
            if scraper_name:
                id_list[new_id]['Custom Scraper Name'] = scraper_name

            old_items = old_by_id[new_id]
            old_doc_url_set = set(extract_urls(old_items.get('Doc URLs', new_item['Doc URLs'])))
            if new_doc_url_set != old_doc_url_set:
                doc_diff = ','.join(list(new_doc_url_set - old_doc_url_set))
                id_list[new_id]['Doc URLs'] = doc_diff

            old_mixed_url_set = set(extract_urls(old_items.get('Mixed URLs', new_item['Mixed URLs'])))
            if new_mixed_url_set != old_mixed_url_set:
                mixed_diff = ','.join(list(new_mixed_url_set - old_mixed_url_set))
                id_list[new_id]['Mixed URLs'] = mixed_diff

            old_search_url_set = set(extract_urls(old_items.get('1st Search Result Page', new_item['1st Search Result Page'])))
            if new_search_url_set != old_search_url_set:
                search_diff = ','.join(list(new_search_url_set - old_search_url_set))
                id_list[new_id]['1st Search Result Page'] = search_diff

        # Reset to the top of the new CSV file in order to re-read it.
        new_csv.seek(0)
        writer = csv.DictWriter(out_csv, fieldnames=new_reader.fieldnames)
        for row in new_reader:
            # We want the diff'ed CSV to be just like the new CSV, but only
            # considering the rows that are different (in the right ways) from
            # the old CSV.
            write_row = dict(row)
            # Always include rows with erroneous ids for safety.
            if not row['id'].isdigit():
                writer.writerow(write_row)
            elif row['id'] in id_list:
                write_row['Custom Scraper Name'] = id_list[row['id']].get('Custom Scraper Name', row['Custom Scraper Name'])
                write_row['Doc URLs'] = id_list[row['id']].get('Doc URLs', row['Doc URLs'])
                write_row['Mixed URLs'] = id_list[row['id']].get('Mixed URLs', row['Mixed URLs'])
                write_row['1st Search Result Page'] = id_list[row['id']].get('1st Search Result Page', row['1st Search Result Page'])

                writer.writerow(write_row)

if __name__ == '__main__':
    main()
