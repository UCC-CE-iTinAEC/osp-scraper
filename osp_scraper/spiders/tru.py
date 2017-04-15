# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TRUSpider(CustomSpider):
    name = "tru"

    start_urls = ["http://www.tru.ca/distance/courses/?p=subject"]

    def parse(self, response):
        # NOTE: Technically the request to the "A-B" tab is made twice, since
        # it's also the landing page.
        tabs = response.css("ul.tabs li a")
        for tab in tabs:
            url = tab.css("::attr(href)").extract_first()
            anchor = " ".join(tab.css("::text").extract_first().split())
            yield scrapy.Request(
                response.urljoin(url),
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        rows = response.css("div.tabs-content table tr")
        for row in rows:
            onclick = row.css("::attr(onclick)").extract_first()
            url = onclick.split("'")[1]
            course_num = row.css("td:first-child strong::text").extract_first()
            course_name = row.css("td:nth-child(2)::text").extract_first()
            anchor = course_num + " " + course_name
            yield (url, anchor)
