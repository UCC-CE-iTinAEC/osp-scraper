# -*- coding: utf-8 -*-

import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class RiosaladoSpider(CustomSpider):
    name = "riosalado"

    start_urls = ["http://www.riosalado.edu/Pages/leftnav/schedule.txt"]

    def parse(self, response):
        terms = sorted(filter(None, response.css("#terms option::attr(value)").getall()))
        yield scrapy.Request(
            "http://www.riosalado.edu/WebServices/Pages/schedule/options.aspx?type=subject",
            meta={
                'terms': terms
            },
            callback=self.parse_for_subjects
        )

    def parse_for_subjects(self, response):
        """
        This method mimics the logic found in the site's javascript.  When used
        together, the parameters 'term1' and 'term2' fetch all courses that
        match a given 'prefix' and occured during 'term1', 'term2' and/or all
        terms in-between.

        Currently, only two terms are available on the site, but this could
        change in the future.
        """
        subj_url = "http://www.riosalado.edu/WebServices/Pages/schedule/sch.aspx"
        subjects = json.loads(response.body_as_unicode())
        term1 = response.meta['terms'][0]
        term2 = response.meta['terms'][-1]
        for subj in subjects:
            yield scrapy.FormRequest(
                subj_url,
                method="GET",
                formdata={
                    'prefix': subj['Prefix'],
                    'term1': term1,
                    'term2': term2
                },
                meta={
                    'title': subj['Subject_area_desc']
                },
                callback=self.parse_for_syllabi
            )

    def parse_for_syllabi(self, response):
        courses = json.loads(response.body_as_unicode())
        for course in courses:
            anchor = " ".join([
                "Term " + course['Term'],
                "Section " + course['Sect'],
                course['Course'],
                course['Title']
            ])

            # NOTE: Many of the syllabi URLs lead to a "syllabus
            # unavailable"-type page.
            yield scrapy.Request(
                course['MiniSyllabusUrl'],
                meta={
                    'depth': 3,
                    'hops_from_seed': 3,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
