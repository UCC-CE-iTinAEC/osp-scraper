# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class MarylhurstSpider(CustomSpider):
    name = "marylhurst"

    start_urls = ["http://my.marylhurst.edu/soc/default.aspx"]

    def parse(self, response):
        terms = response.css("#termDropdown option")
        for term in terms:
            value = term.css("::attr(value)").extract_first()
            anchor = term.css("::text").extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'termDropdown': value,
                    'filterDropdown': "ALL+DEPARTMENTS"
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        pass

    def extract_links(self, response):
        pass
