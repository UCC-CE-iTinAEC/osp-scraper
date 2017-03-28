# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TVCCSpider(CustomSpider):
    name = "tvcc"

    def start_requests(self):
        start_url = "http://webapps.tvcc.edu/ClassSched1/?viewSyllabus=false"

        def get_terms_codes(response):
            for option in response.css("select[name='ctl00$MainContent$ddlSems'] option"):
                term_code = option.css("option::attr(value)").extract_first()
                if term_code:
                    name = option.css("option::text").extract_first()
                    yield scrapy.FormRequest.from_response(
                        response,
                        formdata={
                            "ctl00$MainContent$ddlSems": term_code,
                        },
                        meta={
                            'source_url': response.url,
                            'source_anchor': name,
                            'depth': 1,
                            'hops_from_seed': 1
                        },
                        callback=self.parse_for_files
                    )

        yield scrapy.Request(start_url, callback=get_terms_codes)

    def extract_links(self, response):
        for row in response.css("#MainContent_tblSyllabus tr"):
            relative_url = row.css("a::attr(href)").extract_first()
            if relative_url:
                url = response.urljoin(relative_url)
                anchor = row.css("a::text").extract_first()
                yield (url, anchor)
