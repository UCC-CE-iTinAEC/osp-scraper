# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class InverHillsSpider(CustomSpider):
    name = "inverhills"

    start_urls = [
        "https://www.inverhills.edu/eforms/ClassSchedule/index.asp",
        "https://www.inverhills.edu/eforms/ClassSchedule/ArchivedTerms/index.asp"
    ]

    def parse(self, response):
        terms = response.css("[name='cboTerm'] option")[1:]
        term_codes = terms.css("option::attr(value)").extract()
        term_names = terms.css("option::text").extract()

        subjects = response.css("[name='cboSubject'] option")
        subject_codes = subjects.css("option::attr(value)").extract()
        subject_names = subjects.css("option::text").extract()

        for term_code, term_name in zip(term_codes, term_names):
            for subject_code, subject_name in zip(subject_codes, subject_names):
                yield scrapy.FormRequest.from_response(
                    response,
                    formid="form1",
                    method="POST",
                    formdata={
                        'cboTerm': term_code,
                        'cboSubject': subject_code
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': term_name + " " + subject_name
                    },
                    callback=self.parse_for_files
                )

    def extract_links(self, response):
        for a_tag in response.css(".pdf"):
            href = a_tag.css("::attr(href)").extract_first()
            title = a_tag.css("::attr(title)").extract_first()
            yield (href, title)
