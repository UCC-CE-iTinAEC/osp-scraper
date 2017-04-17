# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class BrevardSpider(CustomSpider):
    name = "brevard"

    start_urls = ["http://web12.easternflorida.edu/ecpr/choice.cfm?CC=1"]

    search_type = "College Credit"
    page = 1

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            meta={
                'depth': 1,
                'hops_from_seed': 1,
                'source_url': response.url,
                'source_anchor': self.search_type + " " + str(self.page),
                'require_files': True
            },
            callback=self.parse_for_courses
        )

    def parse_for_courses(self, response):
        for item in self.parse_for_files(response):
            yield item

        results = response.css("table table")[0].css("tr")[1:]
        next_url = response\
            .css("form > table:last-child a:last-child::attr(href)")\
            .extract_first()
        if results and next_url:
            self.page += 1
            anchor = self.search_type + " Search " + str(self.page)
            yield scrapy.Request(
                response.urljoin(next_url),
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'require_files': True
                },
                callback=self.parse_for_courses
            )
        elif self.search_type == "College Credit":
            self.search_type = "Continuing Education"
            self.page = 1
            # Reset the fingerprints set, so that the scraper can revisit pages
            # with the same url now that the cookies have been changed.
            self.crawler.engine.slot.scheduler.df.fingerprints = set()
            yield scrapy.Request(
                "http://web12.easternflorida.edu/ecpr/choice.cfm?CE=1"
            )

    def extract_links(self, response):
        for row in response.css("table table")[0].css("tr")[1:]:
            url = row.css(".text10::attr(href)").extract_first()
            if url:
                anchor = row.css(".text10::text").extract_first()
                yield (url, anchor)
