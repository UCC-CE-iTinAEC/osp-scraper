# -*- coding: utf-8 -*-

import itertools

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SheridanSpider(CustomSpider):
    name = "sheridanc"

    start_urls = ["https://ulysses.sheridanc.on.ca/coutline/results.jsp"]

    def parse(self, response):
        current_year = int(response.headers['Date'].split()[3])
        years = range(2000, current_year + 2)
        seasons = response.css("#season option::attr(value)").extract()
        programs = response.css("#program_ps option::attr(value)").extract()

        for year, season, program in itertools.product(years, seasons, programs):
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'program_ps': program,
                    'program': program,
                    'season': season,
                    'year': str(year)
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for row in response.css("#detail_table tr"):
            relative_url = row.css("a::attr(href)").extract_first()
            if relative_url:
                url = response.urljoin(relative_url)
                cell_contents = row.css("::text").extract()
                anchor = self.clean_whitespace(" ".join(cell_contents))
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
