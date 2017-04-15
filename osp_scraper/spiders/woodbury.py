# -*- coding: utf-8 -*-

import itertools
import scrapy

from ..spiders.CustomSpider import CustomSpider

class WoodburySpider(CustomSpider):
    name = "woodbury"
    allowed_domains = ["woodbury.edu"]

    def start_requests(self):
        start_url = "https://go.woodbury.edu/syllabus/view.aspx"

        def get_years(response):
            years = response.css("select#dYear option::attr(value)").extract()
            terms = response.css("select#dTerm option::attr(value)").extract()
            for year, term in itertools.product(years, terms):
                yield scrapy.FormRequest.from_response(
                    response,
                    method="POST",
                    formdata={
                        'dYear': year,
                        'dTerm': term,
                        'bRefresh': "Show+Syllabus"
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': year + ' ' + term
                    },
                    callback=self.parse_for_files
                )

        yield scrapy.Request(start_url, callback=get_years)

    def extract_links(self, response):
        tags = response.css("#lCourses a")
        for tag in tags:
            url = tag.css("a::attr(href)").extract_first()
            url = response.urljoin(url)
            anchor = tag.css("a::text").extract_first()
            yield (url, anchor)
