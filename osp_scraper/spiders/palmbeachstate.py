# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class PalmBeachStateSpider(CustomSpider):
    name = 'palmbeachstate'

    start_urls = ["http://www.palmbeachstate.edu/pf/"]

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formid='form1',
            formdata={
                'ctl00$ContentPlaceHolder1$btnPeopleSearch': "Search"
            },
            callback=self.parse_for_people
        )

    def parse_for_people(self, response):
        for row in response.css("#ContentPlaceHolder1_gvResults tr"):
            relative_url = row.css("a::attr(href)").extract_first()
            if relative_url:
                url = response.urljoin(relative_url)
                name = row.css("a::text").extract_first()
                yield scrapy.Request(
                    url,
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': name
                    },
                    callback=self.parse_for_files
                )

    def extract_links(self, response):
        for row in response.css("tr"):
            relative_url = row.css("a::attr(href)").extract_first()
            if relative_url and "Syllabus" in relative_url:
                url = response.urljoin(relative_url)
                row_text = " ".join(row.css("::text").extract())
                anchor = self.clean_whitespace(row_text)
                yield (url, anchor)
