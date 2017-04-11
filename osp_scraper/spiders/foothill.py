# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class FoothillSpider(CustomSpider):
    name = "foothill"

    start_urls = ["http://www.foothill.edu/cms/outlines"]

    def parse(self, response):
        for dept in response.css("#Department option::attr(value)").extract():
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'Department': dept
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        # First and last two rows aren't courses
        for row in response.css("form tr")[1:-2]:
            course_id = row.css("input::attr(value)").extract_first()
            course_name = row.css("td:last-child b::text").extract_first()
            anchor = course_id + " " + course_name
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'record': course_id
                },
                meta={
                    'depth': 2,
                    'hops_from_seed': 2,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
