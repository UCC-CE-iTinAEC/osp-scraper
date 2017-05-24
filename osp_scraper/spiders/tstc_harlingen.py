# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TSTCHarlingenSpider(CustomSpider):
    name = "tstc_harlingen"

    start_urls = ["http://www.harlingen.tstc.edu/services/courseschedules.aspx"]

    def parse(self, response):
        semesters = response.css("#ddlSemester option::attr(value)").getall()
        dept_values = response.css("#ddlDept option::attr(value)").getall()
        dept_names = response.css("#ddlDept option::text").getall()

        for semester in semesters:
            for dept_value, dept_name in zip(dept_values, dept_names):
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata={
                        'ddlSemester': semester,
                        'ddlDept': dept_value
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': semester + " " + dept_name,
                        'require_files': True
                    },
                    callback=self.parse_for_files
                )

    def extract_links(self, response):
        for row in response.css("#tblSchedule tr")[2:]:
            url = row.css("a[title='Course Syllabus']::attr(href)").get()
            if url:
                anchor = " ".join([
                    response.meta["source_anchor"],
                    *row.css("td")[:2].css("::text").getall()
                ])
                yield (url, anchor)
