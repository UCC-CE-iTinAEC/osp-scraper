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
        table_rows = response.css("table#GridView1 tr")[1:]
        for row in table_rows:
            a_tag = row.css("td:nth-child(5)>a")
            url = a_tag.css("::attr(href)").extract_first()
            if url:
                a_tag_anchor = a_tag.css("::text").extract_first()
                crn, course, section = row.css("td ::text").extract()[0:3]
                anchor = " ".join([crn, course, section, a_tag_anchor])
                yield scrapy.Request(
                    url,
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )
