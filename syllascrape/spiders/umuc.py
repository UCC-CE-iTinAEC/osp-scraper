# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class UMUCSpider(CustomSpider):
    name = "umuc"
    allowed_domains = ["umuc.edu", "api.apidapter.com", "umuc.campusconcourse.com"]

    start_urls = [
        "http://webapps.umuc.edu/soc/asia.cfm?fAcad=UGRD",
        "http://webapps.umuc.edu/soc/asia.cfm?fAcad=GR4T",
        "http://webapps.umuc.edu/soc/asia.cfm?fAcad=UBSU",
    ]

    def parse(self, response):
        sessions = []
        for option in response.css("#soc-session option"):
            value = option.css("option::attr(value)").extract_first()
            text = self.clean_whitespace(option.css("option::text").extract_first())
            sessions.append((value, text))

        locations = ["ALL", "WEB|ADLPH"]

        for location in locations:
            for session_value, session_text in sessions:
                    yield scrapy.FormRequest(
                        response.url,
                        formdata={
                            "fSess": session_value,
                            "fLoc": location,
                            "fFetchRows": "99999",
                        },
                        method='GET',
                        meta={
                            "depth": 1,
                            "hops_from_seed": 1,
                            "source_url": response.url,
                            "source_anchor": session_text,
                        },
                        callback=self.parse_for_syllabi
                    )

    def parse_for_syllabi(self, response):
        for tag in response.css("#soc-list a.print_hide"):
            url = tag.css("a::attr(href)").extract_first()
            anchor = tag.css("a::text").extract_first()
            if url and anchor == "Syllabus":
                yield scrapy.Request(
                    url,
                    meta={
                        'source_url': response.url,
                        'source_anchor': anchor,
                        'depth': response.meta['depth'] + 1,
                        'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    },
                    callback=self.submit_form
                )

    def submit_form(self, response):
        url = response.css('form::attr(action)').extract_first()
        method = response.css('form::attr(method)').extract_first() or "GET"
        formdata = {}
        for field in response.css('form input[type=hidden]'):
            name = field.css('input::attr(name)').extract_first()
            value = field.css('input::attr(value)').extract_first()
            if name and value:
                formdata[name] = value

        if url and formdata:
            yield scrapy.FormRequest(
                url,
                formdata=formdata,
                method=method,
                meta=response.meta,
                callback=self.parse_for_files
            )
