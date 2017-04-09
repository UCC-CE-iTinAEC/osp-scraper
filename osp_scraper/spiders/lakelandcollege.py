# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class LakeLandCollegeSpider(CustomSpider):
    name = 'lakelandcollege'

    start_urls = ["https://www.lakelandcollege.edu/academic-programs/"]

    def parse(self, response):
        term_codes = response.css("select[name='term_year']")\
            .css("option::attr(value)")\
            .extract()[1:]

        for term_code in term_codes:
            yield scrapy.FormRequest(
                response.url,
                method='POST',
                formdata={
                    'name_submit': "Search",
                    'term_year': term_code
                },
                callback=self.parse_for_programs
            )

    def parse_for_programs(self, response):
        for a_tag in response.css("table a"):
            relative_url = a_tag.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            yield scrapy.Request(url, callback=self.parse_for_courses)

    def parse_for_courses(self, response):
        for a_tag in response.css("table a.fancyiframe1"):
            relative_url = a_tag.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            anchor = a_tag.css("a::text").extract_first()
            yield scrapy.Request(
                url,
                meta={
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'depth': 3,
                    'hops_from_seed': 3
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        # xpath is necessary here because the response body is malformed HTML
        relative_url = response.xpath("//a").css("::attr(href)").extract_first()

        if relative_url:
            url = response.urljoin(relative_url)
            anchor = response.xpath("//h3").css("h3::text").extract_first()
            yield (url, anchor)
