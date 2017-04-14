# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TempleSpider(CustomSpider):
    name = "temple"
    allowed_domains = ["temple.edu"]

    def start_requests(self):
        get_syllabi_url = "https://math.temple.edu/cgi-bin/get_syllabi"

        def get_years(response):
            years = response.css("#year option::attr(value)").extract()[1:]

            for year in years:
                yield scrapy.Request(
                    response.url + "?year=" + year,
                    callback=get_semesters
                )

        def get_semesters(response):
            semesters = response.css("#semester option::attr(value)")\
                .extract()[1:]

            for semester in semesters:
                yield scrapy.Request(
                    response.url + "&semester=" + semester,
                    callback=get_courses
                )

        def get_courses(response):
            courses = response.css("#course option::attr(value)").extract()[1:]

            for course in courses:
                yield scrapy.Request(
                    response.url + "&course=" + course,
                    callback=get_sections
                )

        def get_sections(response):
            sections = response.css("#section option::attr(value)").extract()[1:]

            for section in sections:
                yield scrapy.Request(
                    response.url + "&section=" + section,
                    callback=self.parse_for_files
                )

        yield scrapy.Request(get_syllabi_url, callback=get_years)
