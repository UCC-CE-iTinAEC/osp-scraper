# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class LSCOSpider(CustomSpider):
    name = "lsco"

    start_urls = ["https://lscossbprod.lsco.edu:9200/rgdb/bwckschd.p_disp_dyn_sched"]

    def parse(self, response):
        terms = response.css("#term_input_id option")[1:]
        for term in terms:
            value = term.css("::attr(value)").extract_first()
            anchor = term.css("::text").extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'p_term': value
                },
                meta={
                    'term': anchor
                },
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
                'sel_attr': ["dummy", "%"]
            },
            meta={
                'term': response.meta['term']
            },
            callback=self.parse_classes
        )

    def parse_classes(self, response):
        for header in response.css("th.ddtitle a"):
            url = header.css("a::attr(href)").extract_first()
            anchor = header.css("a::text").extract_first()
            yield scrapy.Request(
                response.urljoin(url),
                meta={
                    'term': response.meta['term']
                },
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
                        'depth': 3,
                        'hops_from_seed': 3,
                        'source_url': response.url,
                        'source_anchor': response.meta['term'] + " " + anchor
                    },
                    callback=self.parse_for_files
                )
                break

    def extract_links(self, response):
        tags = response.css("td.dddefault a::attr(href)")
        syllabus_link = tags.re_first(r'(^.*syllabus.*$)')
        if syllabus_link:
            anchor = response.css("th.ddlabel::text").extract_first()
            yield (syllabus_link, anchor)
            return
