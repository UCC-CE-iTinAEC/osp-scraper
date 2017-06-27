# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ITTraleeSpider(CustomSpider):
    name = "ittralee"

    start_urls = [
        "http://www.ittralee.ie/en/ModDetails/PHPfunction/getsearchfields.php?searchMode=subject"
    ]

    def parse(self, response):
        base_url = "http://www.ittralee.ie/en/ModDetails/PHPfunction/module-search-results.php"

        subjs = response.css("#subj_code option")
        for subj in subjs:
            subj_value = subj.css("::attr(value)").get()

            yield scrapy.FormRequest(
                base_url,
                method="GET",
                formdata={
                    'searchMode': 'subject',
                    'code': subj_value,
                    'level': 'all'
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        base_url = "http://www.ittralee.ie/en/ModDetails/view-complete-module.php"

        rows = response.css("table.select-module tr")
        for row in rows:
            a_tag = row.css("a")
            if a_tag:
                rel_url = a_tag.css("::attr(href)").get()
                anchor = " ".join(row.css("td ::text").getall())

                yield scrapy.Request(
                    urljoin(base_url, rel_url),
                    meta={
                        'depth': 2,
                        'hops_from_seed': 2,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )
