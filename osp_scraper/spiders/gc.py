# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class GCSpider(CustomSpider):
    name = "gc"

    start_urls = ["http://www2.gc.edu/Syllabi/syllabi.asp"]

    def parse(self, response):
        for term in response.css("#term option::attr(value)").extract():
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'term': term
                },
                callback=self.parse_for_subjects
            )

    def parse_for_subjects(self, response):
        for subject in response.css("#subject option::attr(value)").extract():
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'subject': subject
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for course in response.css("#course option::attr(value)").extract():
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'course': course
                },
                callback=self.parse_for_sections
            )

    def parse_for_sections(self, response):
        term = response.css("#term::attr(value)").extract_first()
        subject = response.css("#subject::attr(value)").extract_first()
        course = response.css("#course::attr(value)").extract_first()
        for option in response.css("#section option"):
            section = option.css("::attr(value)").extract_first()
            anchor = " ".join([term, subject, course, section])
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'section': section
                },
                meta={
                    'depth': 4,
                    'hops_from_seed': 4,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
