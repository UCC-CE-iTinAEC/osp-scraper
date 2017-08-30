# -*- coding: utf-8 -*-

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
                    yield scrapy.Request(
                        row.get('Document Url'),
                        meta={
                            'depth': 0,
                            'hops_from_seed': 0,
                            'source_url': source,
                            'source_anchor': ""
                        },
                        callback=self.parse_for_files
                    )
