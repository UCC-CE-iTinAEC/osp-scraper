# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TSTCSpider(CustomSpider):
    name = "tstc"

    start_urls = [
        "http://iam.tstc.edu/syl/DeptInsVdrpdwnWSYLactiveworkdsURLwilliamson.cfm",
        "http://iam.tstc.edu/syl/DeptInsVdrpdwnWSYLactiveworkdsURLwaco.cfm"
    ]

    def parse(self, response):
        semesters = response.css("select[name='filen'] option::attr(value)")\
            .getall()

        for semester in semesters:
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'filen': semester
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for row in response.css("tr"):
            # Onclick attribute is of the form:
            # opn('<url>','','scrollbars=yes,resizable=yes,width=1200,height=900')
            onclick = row.css("a::attr(onclick)").get()
            if onclick:
                url = onclick.split("'")[1]
                anchor = " ".join(row.css("td")[:2].css("::text").getall())
                yield response.follow(
                    url,
                    meta={
                        'depth': 2,
                        'hops_from_seed': 2,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )
