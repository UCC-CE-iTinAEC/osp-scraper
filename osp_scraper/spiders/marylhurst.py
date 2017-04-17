# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class MarylhurstSpider(CustomSpider):
    name = "marylhurst"

    start_urls = ["http://my.marylhurst.edu/soc/default.aspx"]

    def parse(self, response):
        terms = response.css("#termDropdown option::attr(value)").extract()
        for term in terms:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'termDropdown': term,
                    'filterDropdown': "ALL DEPARTMENTS"
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        a_tags = response.css("#scheduleTable tr a")
        for a_tag in a_tags:
            # onclick is of the form:
            # return showCrsDescription('<code>', '<term>');
            code, term = a_tag.css("::attr(onclick)").re("'(.*?)'")
            course_name = a_tag.css("::text").extract_first()
            yield scrapy.FormRequest(
                "http://my.marylhurst.edu/soc/Webservice.asmx/GetCourseDescription",
                method="POST",
                formdata={
                    'CourseCode': code + "_" + term
                },
                meta={
                    'source_anchor': code + " " + course_name
                },
                callback=self.parse_for_syllabus_link
            )

    def parse_for_syllabus_link(self, response):
        # Response is xml with escaped html within.
        url = response.css("*").re_first("href='(.*?)'")
        yield scrapy.Request(
            url,
            meta={
                'depth': 2,
                'hops_from_seed': 2,
                'source_url': response.url,
                'source_anchor': response.meta["source_anchor"]
            },
            callback=self.parse_for_files
        )

    def extract_links(self, response):
        # Most courses have an HTML syllabus, but a few link to files instead.
        for a_tag in response.css("a"):
            url = a_tag.css("::attr(href)").extract_first()
            a_text = a_tag.css("::text").extract_first()
            if "syllabus" in a_text.lower():
                anchor = response.meta['source_anchor'] + " " + a_text
                yield (url, anchor)
