# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ILCCSpider(CustomSpider):
    name = "ecollege"

    start_urls = ["https://secure.ecollege.com/iowacc/index.learn?action=Catalog"]

    def parse(self, response):
        for option in response.css("form input[type='Radio']"):
            term_code = option.css("::attr(value)").extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                formcss="#gbContent form",
                formdata={
                    'SID': term_code
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for row in response.css('table+table tr'):
            url = row.css('td:last-child a::attr(href)').extract_first()
            if url:
                anchor = " ".join(row.css('::text').extract())
                yield scrapy.Request(
                    url,
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )
