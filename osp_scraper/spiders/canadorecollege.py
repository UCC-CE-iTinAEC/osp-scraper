# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class CanadoreCollegeSpider(CustomSpider):
    name = 'canadorecollege'

    start_urls = ["http://canadorecollege.ca/course-outlines"]

    def parse(self, response):
        courses = response.css("#lstcourses option::attr(value)").extract()
        for course in courses:
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'lstcourses': course
                },
                method="POST",
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': course
                },
                # For this site, formdata is usually submitted automatically via
                # javascript, so disable clicking.
                dont_click=True,
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        tags = response.css("#outlines a")
        for tag in tags:
            rel_url = tag.css("a::attr(href)").extract_first()
            url = response.urljoin(rel_url)
            anchor = tag.css("a::text").extract_first()
            yield (url, anchor)
