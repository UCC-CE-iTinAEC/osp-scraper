# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class HowardSpider(CustomSpider):
    """
    Many of the requests generated seem to lead to 500 errors, but there was no
    obvious way to identify them without performing the request.  As they are
    unsuccessful status codes, they won't be saved.
    """

    name = "howard"

    start_urls = ["https://www.howard.edu/syllabi/syllabi2/search.aspx"]

    def parse(self, response):
        schools = response\
            .css("#_ctl0_ContentPlaceHolder1_SCHOOL option::attr(value)")\
            .extract()[1:]
        for school in schools:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    '_ctl0:ContentPlaceHolder1:SCHOOL': school
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': school,
                    'require_files': True
                },
                callback=self.parse_results
            )

    def parse_results(self, response):
        for row in response.css("table tr"):
            relative_url = row.css("td a::attr(href)")\
                .re_first(r"'(sylldisp.*)'")
            if relative_url:
                anchor = row.css("td:nth-child(2)::text").extract_first()
                yield scrapy.Request(
                    response.urljoin(relative_url),
                    meta={
                        'depth': 2,
                        'hops_from_seed': 2,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )

        # Some search results link directly to files
        for item in self.parse_for_files(response):
            yield item

    def extract_links(self, response):
        for row in response.css("table tr"):
            file_url = row.css("td a::attr(href)")\
                .re_first(r"'(syllabus_download.*)'")
            if file_url:
                anchor = row.css("td:nth-child(2)::text").extract_first()
                yield (file_url, anchor)
