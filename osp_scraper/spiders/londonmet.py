# -*- coding: utf-8 -*-

import itertools

import scrapy

from ..spiders.CustomSpider import CustomSpider

class LondonmetSpider(CustomSpider):
    name = "londonmet"

    start_urls = ["https://intranet.londonmet.ac.uk/module-catalogue/"]

    def parse(self, response):
        # NOTE: The 0th option has value "ALL" and text "North and City", and so
        # may cover several or all other options.
        locations = response.css("#teachinglocation option")
        years = response.css("#academicyear option::attr(value)").getall()
        for location, year in itertools.product(locations, years):
            location_value = location.css("::attr(value)").get()
            location_anchor = location.css("::text").get()
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'teachinglocation': location_value,
                    'moduleperiod': "ALL",
                    'moduletime': "ALL",
                    'modulelevel': "ALL",
                    'modulestatus': "ALL",
                    'academicyear': year
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': location_anchor + " " + year
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        rows = response.css("table.searchresults tr")
        for row in rows:
            a_tag = row.css("a")
            if a_tag:
                url = a_tag.css("::attr(href)").get()
                course_code = a_tag.css("::text").get()
                title = row.css(":nth-child(2)::text").get()
                anchor = " ".join([
                    response.meta['source_anchor'],
                    course_code,
                    title
                ])

                yield (url, anchor)
