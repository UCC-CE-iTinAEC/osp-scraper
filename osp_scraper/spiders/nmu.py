# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class NMUSpider(CustomSpider):
    name = "nmu"

    start_urls = [
        "http://webb.nmu.edu/Webb/ArchivedHTML/Education/state/syllabi.htm",
        "http://webb.nmu.edu/Webb/ArchivedHTML/Education/state/outlines.htm"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'depth': 0,
                    'hops_from_seed': 0,
                    'source_url': url,
                    'source_anchor': ''
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        # The first `option` tag of each dropdown menu is a header, so skip it.
        courses = response.css("select option:not(:first-child)")
        for course in courses:
            rel_url = course.css("option::attr(value)").extract_first()
            url = response.urljoin(rel_url)
            anchor = course.css("option::text").extract_first()
            anchor = ' '.join(anchor.split())
            yield (url, anchor)
