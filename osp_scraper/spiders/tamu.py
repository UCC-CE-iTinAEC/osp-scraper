# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TAMUSpider(CustomSpider):
    name = 'tamu'

    start_urls = ["https://compass-ssb.tamu.edu/pls/PROD/bwckschd.p_disp_dyn_sched"]

    def parse(self, response):
        for option in response.css("#term_input_id option")[1:]:
            term_value = option.css("::attr(value)").extract_first()
            term_text = option.css("::text").extract_first()

            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'p_term': term_value
                },
                meta={
                    'term_value': term_value,
                    'term_text': term_text
                },
                callback=self.parse_for_subjects
            )

    def parse_for_subjects(self, response):
        for option in response.css("#subj_id option"):
            subject_value = option.css("::attr(value)").extract_first()
            subject_text = option.css("::text").extract_first()

            anchor = subject_text + " " + response.meta['term_text']

            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'term_in': response.meta["term_value"],
                    'sel_subj': ["dummy", subject_value],
                    'sel_schd': ["dummy", "%"],
                    'sel_insm': ["dummy", "%"],
                    'sel_camp': ["dummy", "%"],
                    'sel_levl': ["dummy", "%"],
                    'sel_instr': ["dummy", "%"],
                    'sel_ptrm': ["dummy", "%"],
                    'sel_attr': ["dummy", "%"]
                },
                meta={
                    'depth': 2,
                    'hops_from_seed': 2,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        for tag in response.css(".datadisplaytable .ddtitle"):
            url = tag.css("th > span > a::attr(href)").extract_first()
            if url:
                anchor = tag.css("th > a::text").extract_first()
                yield (url, anchor)
