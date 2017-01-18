# -*- coding: utf-8 -*-

import scrapy
from ..items import PageItem 

class CurricunetSpider(scrapy.spiders.Spider):
    name = "curricunet"
    allowed_domains = ["curricunet.com"]

    start_urls = [
        "http://www.curricunet.com/sac/search/course/",
    ]

    def start_requests(self):
        def start_form_requests(response):
            options = response.css("select.slct option")
            for option in options:
                anchor = option.css("option::text").extract_first()
                value = option.css("option::attr(value)").extract_first()
                yield scrapy.FormRequest(
                    response.url + "course_search_result.cfm",
                    formdata={
                        "status":"1",
                        "subject_area":"3",
                        "course_number":"",
                        "course_title":"",
                        "colleges_id":"1",
                        "OK":"OK",
                    },
                    method='POST',
                    meta={
                        "depth": 1,
                        "hops_from_seed": 1,
                        "source_url": start_url,
                        "source_anchor": anchor,
                    },
                    callback=self.parse
                )

        for url in CurricunetSpider.start_urls:
            yield scrapy.Request(url, callback=start_form_requests)

    def parse_results_page(self, response):
        results_table_string = response.re_first(r'<table.*?>Course Search Results<.*?</table>')
        results_table = Selector(text=results_table_string)
        results_rows = results_table.css("tr")
        for row in results_rows:
            relative_url = row.css("td.fld a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            anchor = row.css("td span::text").extract_first()
            yield scrapy.Request(
                url,
                meta={
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                }
            )

    def parse(self, response):
        yield PageItem(
            url=response.url,
            content=response.body,
            headers=response.headers,
            status=response.status,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
            depth=response.meta.get('depth'),
            hops_from_seed=response.meta.get('hops_from_seed')
        )
