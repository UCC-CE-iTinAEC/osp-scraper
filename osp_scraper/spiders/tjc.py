# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TJCSpider(CustomSpider):
    name = 'tjc'

    start_urls = ["https://ssbprod2012.tjc.edu/dbServer_PROD/sig_view_crse.p_search"]

    def parse(self, response):
        for option in response.css("select option"):
            term_value = option.css("option::attr(value)").extract_first()
            yield scrapy.FormRequest(
                response.url,
                formdata={
                    'pi_term_code': term_value,
                    'pi_subj': ""
                },
                method='POST',
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for a_tag in response.css("a:first-child"):
            relative_url = a_tag.css("a::attr(href)").extract_first()
            if relative_url:
                url = response.urljoin(relative_url)
                anchor = a_tag.css("a::text").extract_first()

                yield scrapy.Request(
                    url,
                    meta={
                        'depth': 2,
                        'hops_from_seed': 2,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )
