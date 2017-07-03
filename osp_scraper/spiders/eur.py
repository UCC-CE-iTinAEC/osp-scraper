# -*- coding: utf-8 -*-

import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class EURSpider(CustomSpider):
    name = "eur"

    start_urls = ["https://courses.eur.nl/statics/faculties.json"]

    def parse(self, response):
        base_url = "https://courses.eur.nl/api/course"
        jsonresponse = json.loads(response.body_as_unicode())

        for faculty in jsonresponse['education']:
            matches = {
                'faculties': [
                    faculty['nameNL'],
                    faculty['nameEN']
                ]
            }

            yield scrapy.FormRequest(
                base_url,
                method="GET",
                formdata={
                    'matches': json.dumps(matches)
                },
                meta={
                    'anchor': faculty['nameEN']
                },
                callback=self.set_num_results_per_page
            )

    def set_num_results_per_page(self, response):
        """
        By default, the list of courses when searching by faculty is limited at
        10 results per response.  We set the limit to the total number of
        results so that we can scrape everything from a single response.
        """
        jsonresponse = json.loads(response.body_as_unicode())

        yield scrapy.FormRequest(
            response.url,
            method="GET",
            formdata={
                'limit': str(jsonresponse['count'])
            },
            meta=dict(response.meta),
            callback=self.parse_for_courses
        )

    def parse_for_courses(self, response):
        base_url = "https://courses.eur.nl/api/course/{0}/pdf?locale=en"
        jsonresponse = json.loads(response.body_as_unicode())

        for course in jsonresponse['items']:
            courseid = course['_id']
            anchor = " ".join([
                response.meta['anchor'],
                courseid,
                course['code'],
                course['name_long'],
                course['year'],
                course['language']['description']
            ])

            yield scrapy.Request(
                base_url.format(courseid),
                meta={
                    'depth': 3,
                    'hops_from_seed': 3,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
