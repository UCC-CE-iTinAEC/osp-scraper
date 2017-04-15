# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class UTRGVSpider(CustomSpider):
    name = "utrgv"

    start_urls = ["https://webapps.utrgv.edu/aa/dm/index.cfm"]

    def parse(self, response):
        for option in response.css("#semester-select option"):
            term_code = option.css("option::attr(value)").extract_first()
            name = option.css("option::text").extract_first()

            yield scrapy.FormRequest(
                response.url,
                formdata={
                    'semester': term_code
                },
                meta={
                    'source_url': response.url,
                    'source_anchor': name,
                    'depth': 1,
                    'hops_from_seed': 1,
                },
                callback=self.parse_results_page
            )

    def parse_results_page(self, response):
        for item in self.parse_for_files(response):
            yield item

        next_relative_url = response.css(".next-table::attr(href)")\
            .extract_first()
        if next_relative_url:
            url = response.urljoin(next_relative_url)
            yield scrapy.Request(
                url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': response.meta['source_anchor']
                },
                callback=self.parse_results_page
            )

    def extract_links(self, response):
        # Many of these files are PDFs saying that no syllabus is available
        for row in response.css(".course-listing tbody tr"):
            relative_url = row.css(".syllabus-icon a::attr(href)")\
                .extract_first()
            if relative_url:
                url = response.urljoin(relative_url)
                anchor = " ".join(row.css("td::text").extract()[:5]).strip()
                yield (url, anchor)
