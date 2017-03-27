# -*- coding: utf-8 -*-

import csv
from itertools import groupby
from operator import itemgetter

from ..spiders.CustomSpider import CustomSpider
from ..items import PageItem

class FileDownloader(CustomSpider):
    name = "file_downloader"

    # Workaround since yielding PageItems from start_requests isn't allowed
    start_urls = ["http://example.com/"]

    def parse(self, response):
        with open(self.csv_file) as file:
            rows = csv.DictReader(file)

            for source, group in groupby(rows, itemgetter('Source Url')):
                meta = {
                    'source_url': source,
                    'source_anchor': "",
                    'depth': 1,
                    'hops_from_seed': 1,
                }

                file_urls = [(row.get('Document Url'), meta) for row in group]

                yield PageItem(
                    url=source,
                    content=b"",
                    headers={},
                    status=200,
                    source_url="",
                    source_anchor="",
                    depth=1,
                    hops_from_seed=1,
                    file_urls=file_urls
                )
