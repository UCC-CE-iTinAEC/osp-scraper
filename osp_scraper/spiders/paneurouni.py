# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class PaneurouniSpider(CustomSpider):
    name = "paneurouni"

    start_urls = ["https://is.paneurouni.com/katalog/index.pl?jak=dle_pracovist"]

    def parse(self, response):
        departments = response.css("#fakulty input::attr(value)").getall()
        years = response.css("#blocks > div")
        for year in years:
            year_code = year.css("input[name='obdobi']::attr(value)").get()
            anchor = year.css("::text").get()

            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'fakulta': departments,
                    'obdobi': year_code
                },
                meta={
                    'anchor': anchor
                },
                callback=self.do_department_search
            )

    def do_department_search(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            formdata={
                # The '0' here searches all departments.
                'ustav': "0",
                'vypsat': "Display courses"
            },
            meta=dict(response.meta),
            callback=self.parse_for_syllabi
        )

    def parse_for_syllabi(self, response):
        a_tags = response.css("a[href^='syllabus']")
        for a_tag in a_tags:
            a_tag_text = a_tag.css("::text").get()
            anchor = response.meta['anchor'] + " " + a_tag_text

            yield response.follow(
                a_tag,
                meta={
                    'depth': 3,
                    'hops_from_seed': 3,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
