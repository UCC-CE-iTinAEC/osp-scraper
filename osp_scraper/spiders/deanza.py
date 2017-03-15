# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class DeAnzaSpider(CustomSpider):
    name = "deanza"

    def start_requests(self):
        start_url = "http://ecms.deanza.edu/deptoutlinespublic.html"

        def get_departments(response):
            for option in response.css("#Dept option"):
                code = option.css("option::attr(value)").extract_first()
                if code:
                    yield scrapy.FormRequest(
                        start_url + "?Dept=" + code,
                        method="POST",
                        formdata={
                            "Dept": code,
                        },
                        callback=parse_department
                    )

        def parse_department(response):
            for row in response.css("table table tr"):
                relative_url = row.css("a::attr(href)").extract_first()
                anchor = row.css("a::text").extract_first()
                if relative_url:
                    url = response.urljoin(relative_url)
                    yield scrapy.Request(
                        url,
                        meta={
                            'source_url': response.url,
                            'source_anchor': anchor,
                            'depth': 1,
                            'hops_from_seed': 1,
                        },
                        callback=self.parse_for_files
                    )

        yield scrapy.Request(start_url, callback=get_departments)
