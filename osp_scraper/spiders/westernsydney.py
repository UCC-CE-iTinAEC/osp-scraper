# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class WesternSydneySpider(CustomSpider):
    name = "westernsydney"

    start_urls = [
        "http://library.westernsydney.edu.au/legacy_support/unit_outline.php"
    ]

    def parse(self, response):
        yield scrapy.FormRequest(
            response.url,
            method="GET",
            formdata={
                'dataaction': "Search"
            },
            meta={
                'depth': 1,
                'hops_from_seed': 1,
                'source_url': response.url,
                'source_anchor': 'Page 1'
            },
            callback=self.parse_for_pages
        )

    def parse_for_pages(self, response):
        for item in self.parse_for_files(response):
            yield item

        pages = response.css("select")[0].css("option::attr(value)").getall()
        for page in pages[1:]:
            anchor = "Page " + page

            yield scrapy.FormRequest(
                response.url,
                method="GET",
                formdata={
                    'thispage': page
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        rows = response.css("#legacy-container > div:not([class=clear])")
        for row in rows:
            rel_url = row.css("a::attr(href)").get()
            anchor = " ".join([
                response.meta['source_anchor'],
                *row.css("::text").getall()
            ])

            yield (rel_url, anchor)
