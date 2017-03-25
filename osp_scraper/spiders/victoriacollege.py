# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class VictoriaCollegeSpider(CustomSpider):
    name = "victoriacollege"

    start_urls = ["https://www.victoriacollege.edu/courseinstructorinformation"]

    def parse(self, response):
        semesters = response.css("a[target='_blank'][title~='Courses']")
        for semester in semesters:
            url = semester.css("::attr(href)").extract_first()
            anchor = semester.css("::text").extract_first()
            yield scrapy.Request(
                url,
                callback=self.parse_subjects
            )

    def parse_subjects(self, response):
        subjects = response.css("select#subj_id option::attr(value)").extract()
        term_in = response.css("input[name='term_in']::attr(value)").extract_first()
        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            formdata={
                'term_in': term_in,
                # The extra 'dummy' here is necessary because apparently the
                # first index of each array is ignored as the POST request
                # is processed.
                'sel_subj': ["dummy"] + subjects,
                'sel_schd': ["dummy", "%"],
                'sel_insm': ["dummy", "%"],
                'sel_camp': ["dummy", "%"],
                'sel_levl': ["dummy", "%"],
                'sel_sess': ["dummy", "%"],
                'sel_instr': ["dummy", "%"],
                'sel_ptrm': ["dummy", "%"],
                'sel_attr': ["dummy", "%"],
            },
            callback=self.parse_classes
        )

    def parse_classes(self, response):
        for header in response.css("th.ddtitle a"):
            url = header.css("a::attr(href)").extract_first()
            anchor = header.css("a::text").extract_first()
            yield scrapy.Request(
                response.urljoin(url),
                callback=self.parse_syllabi
            )

    def parse_syllabi(self, response):
        anchor = response.css("th.ddlabel::text").extract_first()
        tags = response.css("td.dddefault a")
        for tag in tags:
            url = tag.css("a::attr(href)").extract_first()
            if "syllabus" in url:
                yield scrapy.Request(
                    response.urljoin(url),
                    meta={
                        'depth': 4,
                        'hops_from_seed': 4,
                        'source_url': response.url,
                        'source_anchor': anchor,
                    },
                    callback=self.parse_for_files
                )
                break

    def extract_links(self, response):
        tags = response.css("td.dddefault a")
        for tag in tags:
            tag_text = tag.css("a::text").extract_first()
            # After executing parse_syllabi, there will either be a link to a
            # syllabus in PDF form or we will have landed on an HTML syllabus.
            # If we are on an HTML syllabus, extract_links will yield nothing.
            if tag_text and "Syllabus" in tag_text:
                url = tag.css("a::attr(href)").extract_first()
                url = response.urljoin(url)
                anchor = response.css("th.ddlabel::text").extract_first()
                yield (url, anchor)
                return
