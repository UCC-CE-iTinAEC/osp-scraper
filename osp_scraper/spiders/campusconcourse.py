# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class CampusConcourseSpider(CustomSpider):
    name = 'campusconcourse'

    def start_requests(self):
        for start_url in self.start_urls:
            yield scrapy.FormRequest(
                start_url,
                method="GET",
                formdata={
                    'search_performed': "1"
                },
                callback=self.parse_for_page_numbers
            )

    def parse_for_page_numbers(self, response):
        pages_text = response.css(".panel-footer label::text").extract_first()
        num_pages = int(pages_text.split()[-1])

        for page in range(num_pages):
            yield scrapy.FormRequest(
                response.url,
                method="GET",
                formdata={
                    'search_performed': "1",
                    'offset': str(page)
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for row in response.css("#results_table tr"):
            anchor = row.css("h4 a::text").extract_first()
            relative_url = row.css("h4 a::attr(href)").extract_first()
            url = response.urljoin(relative_url)

            yield scrapy.Request(
                url,
                meta={
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                },
                callback=self.parse_for_files
            )
