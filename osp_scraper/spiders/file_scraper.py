import csv
from itertools import groupby
from operator import itemgetter

import scrapy

from ..spiders.CustomSpider import CustomSpider


class FileDownloader(CustomSpider):
    name = "file_downloader"

    def start_requests(self):
        with open(self.csv_file) as file:
            rows = csv.DictReader(file)

            for source, group in groupby(rows, itemgetter('Source Url')):
                for row in group:
                    # In OutWit CSVs, target URLs may be located in either the
                    # 'Document Url' or 'Page Url' columns.
                    url = row.get('Document Url') or row.get('Page Url')
                    yield scrapy.Request(
                        url,
                        meta={
                            'source_url': source,
                            'source_anchor': ""
                        },
                        callback=self.parse_for_files
                    )
