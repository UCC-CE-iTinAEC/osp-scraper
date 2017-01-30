# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class PSUSpider(CustomSpider):
    name = "psu"
    allowed_domains = ["psu.edu"]

    start_urls = ["http://www.altoona.psu.edu/syllabi/"]

    def parse(self, response):
        view1_url = "http://www.altoona.psu.edu/syllabi/view1.php"

        course_abbreviations = response.css("#course_abbr option::text").extract()
        for course in course_abbreviations:
            yield scrapy.FormRequest(
                view1_url,
                formdata={
                    "course_abbr": course,
                },
                method='POST',
                meta={
                    "depth": 1,
                    "hops_from_seed": 1,
                    "source_url": response.url,
                    "source_anchor": "",
                },
                callback=self.get_semester_urls
            )

    def get_semester_urls(self, response):
        semester_tags = response.css("#main ul li a")
        for tag in semester_tags:
            relative_url = tag.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            anchor = tag.css("a::text").extract_first()
            yield scrapy.Request(
                url,
                meta={
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        title_tags = response.css("table.data tbody td:nth-child(3) a")
        for tag in title_tags:
            relative_url = tag.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            anchor = tag.css("a::text").extract_first()

            yield url, anchor
