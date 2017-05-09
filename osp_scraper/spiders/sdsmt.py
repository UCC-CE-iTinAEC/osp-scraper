# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SDSMTSpider(CustomSpider):
    """
    The search for this site can be done by course abbreviations, which are
    available in a table on a separate page.
    """
    name = "sdsmt"

    start_urls = ["http://ecatalog.sdsmt.edu/content.php?catoid=14&navoid=2598"]

    def parse(self, response):
        search_url = "https://sdmines.sdsmt.edu/cgi-bin/global/tech_search_dir_syllabus.cgi"

        rows = response.css("td.block_content table table tr")
        for row in rows[2:]:
            abbrev = self.clean_whitespace(
                        row.css("td:first-child::text").extract_first())
            anchor = row.css("td:nth-child(2)::text").extract_first()
            yield scrapy.FormRequest(
                search_url,
                method="POST",
                formdata={
                    'submitbtn': "Search",
                    'search': abbrev,
                    'termtype': "all"
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        rows = response.css("table.table tr")
        for row in rows[1:]:
            rel_url = row.css("td:nth-child(4) a::attr(href)").extract_first()
            url = response.urljoin(rel_url)
            anchor = " ".join(row.css("::text").extract())

            yield (url, anchor)
