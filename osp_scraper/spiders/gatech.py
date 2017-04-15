# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class GATechSpider(CustomSpider):
    name = "gatech"

    start_urls = [
        "https://inta.gatech.edu/courses",
        "http://www.econ.gatech.edu/courses",
        "http://www.lmc.gatech.edu/courses",
        "http://www.spp.gatech.edu/courses",
        "http://www.modlangs.gatech.edu/courses"
    ]

    def parse(self, response):
        for option in response.css("select[name='iacTermcode'] option"):
            code = option.css("option::attr(value)").extract_first()
            name = option.css("option::text").extract_first()

            yield scrapy.FormRequest(
                response.url,
                method="POST",
                formdata={
                    'iacTermcode': code
                },
                meta={
                    'source_url': response.url,
                    'source_anchor': name,
                    'depth': 1,
                    'hops_from_seed': 1,
                },
                callback=self.parse_for_files,
            )

    def extract_links(self, response):
        for row in response.css("table tr"):
            relative_url = row.css("td:last-child a::attr(href)").extract_first()
            if relative_url:
                url = response.urljoin(relative_url)
                anchor = row.css("td:first-child::text").extract_first()
                yield (url, anchor)
