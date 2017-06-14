# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TalisSpider(CustomSpider):
    name = "talis"

    def start_requests(self):
        for url in self.database_urls:
            # Search for anything with a space in it
            yield scrapy.Request(
                urljoin(url, "/search.html?q=+"),
                meta={
                    'depth': 0,
                    'hops_from_seed': 0
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for a_tag in response.css("#search_results_lists ol a"):
            anchor = a_tag.css("::text").get()
            yield response.follow(
                a_tag,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

        next_url = response.css("#search_results_lists .pagination")\
            .css("li:nth-child(3) a::attr(href)")\
            .get()
        if next_url:
            yield response.follow(
                next_url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_courses
            )
