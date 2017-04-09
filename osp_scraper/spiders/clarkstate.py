# -*- coding: utf-8 -*-

import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ClarkStateSpider(CustomSpider):
    name = "clarkstate"

    start_urls = [
        "https://www.clarkstate.edu/academics/class-syllabi/archived-syllabi/"
    ]

    def parse(self, response):
        subjects_url = "https://www.clarkstate.edu/api/syllabus/subjects"

        terms = response.css("#term option::attr(value)").extract()
        for term in terms:
            yield scrapy.FormRequest(
                subjects_url,
                method="GET",
                headers={
                    'Accept': "application/json"
                },
                formdata={
                    'term': term,
                    'archives': "true"
                },
                meta={
                    'term': term
                },
                callback=self.parse_for_subjects
            )

    def parse_for_subjects(self, response):
        search_url = "https://www.clarkstate.edu/api/syllabus/index"

        subjects = json.loads(response.body)['Items']
        for subject in subjects:
            yield scrapy.FormRequest(
                search_url,
                formdata={
                    'term': response.meta['term'],
                    'subject': subject['Id'],
                    'archives': "true"
                },
                method="GET",
                headers={
                    'Accept': "application/json"
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        syllabus_url = "http://res.clarkstate.edu/Syllabus/ViewSyllabus.aspx"
        courses = json.loads(response.body)

        for course in courses:
            for section in course['sections']:
                if course['courseTitle']:
                    yield scrapy.FormRequest(
                        syllabus_url,
                        formdata={
                            'Course': section['id'],
                            'Term': section['term'],
                            'Archive': "1"
                        },
                        method="GET",
                        meta={
                            'depth': 1,
                            'hops_from_seed': 1,
                            'source_url': response.url,
                            'source_anchor': course['courseTitle']
                        },
                        callback=self.parse_for_files
                    )
