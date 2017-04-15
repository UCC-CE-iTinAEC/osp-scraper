# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class AmherstSpider(CustomSpider):
    name = "amherst"

    start_urls = ["https://www.amherst.edu/course_scheduler"]

    def parse(self, response):
        terms = response.css(".form-item-termid option::attr(value)").extract()

        for term in terms:
            yield scrapy.FormRequest.from_response(
                response,
                formid="academics-schedule-search",
                formdata={
                    'termid': term
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for a_tag in response.css(".sched-results tr td:nth-child(3) a"):
            anchor = a_tag.css("::text").extract_first()
            relative_url = a_tag.css("::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            yield scrapy.Request(
                url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

        relative_next_url = response.css(".pager-next a::attr(href)")\
            .extract_first()
        if relative_next_url:
            next_url = response.urljoin(relative_next_url)
            yield scrapy.Request(
                url=next_url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_courses
            )
