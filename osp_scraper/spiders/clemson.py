# -*- coding: utf-8 -*-

import itertools
import scrapy

from ..spiders.CustomSpider import CustomSpider

class ClemsonSpider(CustomSpider):
    name = "clemson"

    def start_requests(self):
        start_url = "https://etpr.app.clemson.edu/repository/syllabus_public.php"
        # Need to answer a captcha.
        # Captcha is always the same (pseudo-captcha).
        yield scrapy.FormRequest(
            start_url,
            formdata={
                'person_ck': 'CLEMSON',
                'check_person': 'Logon',
            },
            method='POST',
            callback=self.parse_for_search_terms
        )

    def parse_for_search_terms(self, response):
        sem_codes = response.css('select[name="semester_selected"] option')\
                            .css('::attr(value)')\
                            .extract()
        # Skip the first entry because it's an empty string.
        disciplines = response.css('select[name="subj_selected"] option')[1:]
        subj_codes = disciplines.css('option::attr(value)').extract()
        for sem_code, subj_code in itertools.product(sem_codes, subj_codes):
            # NOTE: from_response doesn't seem to work for some reason?
            yield scrapy.FormRequest(
                response.url,
                formdata={
                    'semester_selected': sem_code,
                    'subj_selected': subj_code,
                    'search_course': 'Load+Course+Files'
                },
                method='POST',
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': sem_code + ' ' + subj_code,
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        tags = response.css('tr td:nth-child(2) div a')
        for tag in tags:
            url = tag.css('a::attr(href)').extract_first()
            url = response.urljoin(url)
            anchor = tag.css('a::text').extract_first()
            yield (url, anchor)
