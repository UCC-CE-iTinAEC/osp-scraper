# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class UGASpider(CustomSpider):
    name = "uga"

    start_urls = ["https://syllabus.uga.edu/Browse.aspx"]

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            formdata={
                # 'DEP1' corresponds to the "View History of Syllabus Files by
                # Department" option.  This seems to give the most yield with
                # the lowest amount of form-work.
                'RadioButtonList1': "DEP1",
                'Button1': "Submit"
            },
            callback=self.parse_for_departments
        )

    def parse_for_departments(self, response):
        departments = response.css("#ddlDepartment option")[1:]
        for dept in departments:
            value = dept.css("::attr(value)").extract_first()
            anchor = dept.css("::text").extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'ddlDepartment': value
                },
                meta={
                    'depth': 2,
                    'hops_from_seed': 2,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                dont_click=True,
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        # Syllabi are stored at the same URL behind javascript links that feed
        # into ASP.NET POST requests.  So, rather than implement extract_links,
        # we yield the response of each POST request into parse_for_files.
        rows = response.css("#gridFileList tr")[1:]
        for row in rows:
            link = row.css("td:nth-child(6) a")
            if link:
                # Links look like this:
                # javascript:__doPostBack('<eventtarget>','<eventargument>')
                eventtarget, eventargument = link.css("::attr(href)")\
                                                 .re(r"'(.*?)'")
                anchor = " ".join([
                    response.meta['source_anchor'],
                    *row.css("td::text").extract()[:3],
                    link.css("::text").extract_first()
                ])
                yield scrapy.FormRequest.from_response(
                    response,
                    method="POST",
                    formdata={
                        '__EVENTTARGET': eventtarget,
                        '__EVENTARGUMENT': eventargument,
                    },
                    meta={
                        'depth': 3,
                        'hops_from_seed': 3,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    dont_click=True,
                    callback=self.parse_for_files
                )
