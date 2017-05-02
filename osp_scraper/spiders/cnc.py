# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class CNCSpider(CustomSpider):
    """
    Every syllabus link on this site is hidden behind a 302 redirect.
    Currently, for whatever reason, requests that redirect are given very low
    priority.  This means that, even though this scraper seems to be functional,
    it takes a very long time to download any files.
    """
    name = "cnc"

    start_urls = ["http://tools.cnc.bc.ca/courseoutlines/Default.aspx"]

    def parse(self, response):
        years = response.css("#YearList option::attr(value)")[1:].extract()
        for year in years:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'YearList': year,
                    'Button1': "Search for Outlines"
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': year,
                    'require_files': True
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        # Skip the first row because it's the table header.
        rows = response.css("#ResultsTable tr")[1:]
        for row in rows:
            link = row.css("td:nth-child(2) a::attr(href)").extract_first()
            scanid = link.split("'")[1]
            outline_url_format = "PreviewScannedOutline.aspx?id={0}"
            url = response.urljoin(outline_url_format.format(scanid))
            # Anchor is course + section + year and term.
            anchor = " ".join(row.css("td>*::text").extract()[0:3])

            yield (url, anchor)
