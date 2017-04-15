# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class NMJCSpider(CustomSpider):
    name = "nmjc"

    start_urls = ["http://www.nmjc.edu/academics/courseschedule.aspx"]

    def parse(self, response):
        terms = response.css("div select#DropDownList1 option")
        for term in terms:
            code = term.css("::attr(value)").extract_first()
            anchor = term.css("::text").extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'DropDownList1': code,
                    'Button4': "All"
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        # Skip the first row, which is the table header.
        table_rows = response.css("table#GridView1 tr td:nth-child(5) a")[1:]
        for row in table_rows:
            link = row.css("::attr(href)").extract_first()
            a_tag_anchor = row.css("::text").extract_first()
            crn = response.css("table#GridView1 tr td:nth-child(1)::text")\
                          .extract_first()
            course = response.css("table#GridView1 tr td:nth-child(2)::text")\
                             .extract_first()
            section = response.css("table#GridView1 tr td:nth-child(3)::text")\
                              .extract_first()
            anchor = " ".join([crn, course, section, a_tag_anchor])
            yield scrapy.Request(
                link,
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
