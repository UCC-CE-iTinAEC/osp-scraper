# -*- coding: utf-8 -*-

import datetime
import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class WesleyanSpider(CustomSpider):
    name = "wesleyan"

    def start_requests(self):
        # Terms are generated with JS on page, so logic is replicated here.
        terms = []
        current_year = datetime.date.today().year % 100
        for year in range(10, current_year+1):
            terms.extend([
                "1"+str(year)+"1", # Spring
                "1"+str(year)+"6", # Summer
                "1"+str(year)+"9" # Fall
            ])

        for term in terms:
            yield scrapy.FormRequest(
                "https://webapps.wesleyan.edu/wapi/v1/public/academic/syllabus",
                method="GET",
                formdata={
                    'term': term
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        courses = json.loads(response.body)

        for course in courses:
            anchor = " ".join([
                course["cid"],
                course["descr"],
                course["term_text"]
            ])
            yield scrapy.Request(
                course["url"],
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
