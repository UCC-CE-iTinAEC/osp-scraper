# -*- coding: utf-8 -*-

import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class BCITSpider(CustomSpider):
    name = "bcit"

    start_urls = ["http://www.bcit.ca/study/outlines/indexajax.php/index/getinitialstate/"]

    def parse(self, response):
        get_subjects_url = "http://www.bcit.ca/study/outlines/indexajax.php/index/loadsubjects/term/{term}"
        terms = json.loads(response.body)["terms"]

        for term in terms:
            meta = {
                "term": term
            }
            url = get_subjects_url.format(**meta)
            yield scrapy.Request(url, meta=meta, callback=self.parse_for_subjects)

    def parse_for_subjects(self, response):
        get_courses_url = "http://www.bcit.ca/study/outlines/indexajax.php/index/loadsubjectcourses/term/{term}/subject/{subject}"
        subjects = json.loads(response.body)

        for subject in subjects:
            meta = dict(response.meta)
            meta["subject"] = subject
            url = get_courses_url.format(**meta)
            yield scrapy.Request(url, meta=meta, callback=self.parse_for_courses)

    def parse_for_courses(self, response):
        get_sections_url = "http://www.bcit.ca/study/outlines/indexajax.php/index/populatecoursetable/term/{term}/course/{course}/subj/{subject}"
        courses = json.loads(response.body)

        for course in courses:
            meta = dict(response.meta)
            meta["course"] = course
            url = get_sections_url.format(**meta)
            yield scrapy.Request(url, meta=meta, callback=self.parse_for_sections)

    def parse_for_sections(self, response):
        get_outline_url = "http://www.bcit.ca/study/outlines/{course_id}"
        rows = response.css('tr')
        for row in rows:
            course_id = row.css('a::attr(href)').extract_first()
            if course_id:
                url = get_outline_url.format(course_id=course_id)
                course_number = row.css('a::text').extract_first()
                anchor = " ".join([
                    response.meta["term"],
                    response.meta["subject"],
                    response.meta["course"],
                    course_number
                ]).strip()

                yield scrapy.Request(
                    url,
                    meta={
                        "depth": 0,
                        "hops_from_seed": 1,
                        "source_url": url,
                        "source_anchor": anchor
                    },
                    callback=self.parse_for_files
                )
