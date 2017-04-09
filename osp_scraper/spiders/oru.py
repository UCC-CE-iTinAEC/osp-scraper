# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ORUSpider(CustomSpider):
    name = "oru"

    start_urls = ["https://syllabi.oru.edu/"]

    def parse(self, response):
        for option in response.css("select[name='term'] option"):
            code = option.css("option::attr(value)").extract_first()
            if code:
                name = option.css("option::text").extract_first()
                yield scrapy.FormRequest(
                    response.url,
                    formdata={
                        'term': code
                    },
                    method="GET",
                    meta={
                        'source_anchor': name
                    },
                    callback=self.parse_for_departments
                )

    def parse_for_departments(self, response):
        for option in response.css("select[name='dept'] option"):
            code = option.css("option::attr(value)").extract_first()
            if code:
                name = option.css("option::text").extract_first()
                anchor = response.meta.get('source_anchor') + " " + name
                yield scrapy.FormRequest(
                    response.url,
                    formdata={
                        'dept': code
                    },
                    method="GET",
                    meta={
                        'source_url': response.url,
                        'source_anchor': anchor,
                        'depth': 1,
                        'hops_from_seed': 1
                    },
                    callback=self.parse_for_files
                )

    def extract_links(self, response):
        print(response.url)
        for tag in response.css(".main-content form a"):
            relative_url = tag.css("a::attr(href)").extract_first()
            if relative_url:
                url = response.urljoin(relative_url)
                anchor = tag.css("a::text").extract_first()
                yield (url, anchor)
