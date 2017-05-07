# -*- coding: utf-8 -*-

import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TXStateSpider(CustomSpider):
    name = "txstate"

    start_urls = ["https://api.hb2504.txstate.edu/py/getdepartments.py"]

    def parse(self, response):
        departments_url = "https://api.hb2504.txstate.edu/py/getcoursesfordepartment.py"
        jsonresponse = json.loads(response.body_as_unicode())
        for dept in jsonresponse['departments']:
            yield scrapy.FormRequest(
                departments_url,
                method="GET",
                formdata={
                    'department': dept
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        courses_url = "https://api.hb2504.txstate.edu/py/getcoursedetails.py"
        jsonresponse = json.loads(response.body_as_unicode())
        for course in jsonresponse['courses']:
            number = course['number']
            title = course['title']
            yield scrapy.FormRequest(
                courses_url,
                method="GET",
                formdata={
                    'course': number
                },
                meta={
                    'title': title,
                    'course': number
                },
                callback=self.parse_for_classes
            )

    def parse_for_classes(self, response):
        classes_url = "https://api.hb2504.txstate.edu/py/getclassesforcourse.py"
        jsonresponse = json.loads(response.body_as_unicode())
        for sem in jsonresponse['semesters']:
            yield scrapy.FormRequest(
                classes_url,
                method="GET",
                formdata={
                    'course': response.meta['course'],
                    'semester': str(sem)
                },
                meta={
                    'title': response.meta['title'],
                    'course': response.meta['course'],
                    'semester': str(sem)
                },
                callback=self.parse_for_syllabi
            )

    def parse_for_syllabi(self, response):
        syllabi_url = "https://api.hb2504.txstate.edu/py/getsyllabus.py"
        jsonresponse = json.loads(response.body_as_unicode())
        for row in jsonresponse['classes']:
            # The json provides a convenient boolean for whether a class has a
            # syllabus available or not.
            if row['syllabus']:
                indexnum = row['indexnum']
                anchor = " ".join([
                    response.meta['course'],
                    row['section'],
                    response.meta['title'],
                    response.meta['semester'],
                    row['instructor']['displayname']
                ])

                yield scrapy.FormRequest(
                    syllabi_url,
                    method="GET",
                    formdata={
                        'class': str(indexnum)
                    },
                    meta={
                        'depth': 3,
                        'hops_from_seed': 3,
                        'source_url':
                            "http://hb2504.txstate.edu/viewcourse.html#" + response.meta['course'],
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )
