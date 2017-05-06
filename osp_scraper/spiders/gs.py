# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class GSSpider(CustomSpider):
    name = "gs"

    start_urls = ["https://www.gs.edu/academics/course-syllabi/"]

    def parse(self, response):
        caspio_link = response.css("#cxkg a:first-child::attr(href)")\
                              .extract_first()
        yield scrapy.Request(
            caspio_link,
            callback=self.enter_search
        )

    def enter_search(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            meta={
                'depth': 1,
                'hops_from_seed': 1,
                'source_url': response.url,
                'source_anchor': 'Page 1',
                'page_num': 1
            },
            callback=self.parse_for_pages
        )

    def parse_for_pages(self, response):
        for item in self.parse_for_files(response):
            yield item

        rel_url = response.css("a[data-cb-name='JumpToNext']::attr(href)")\
                          .extract_first()
        if rel_url:
            url = response.urljoin(rel_url)
            page_num = response.meta['page_num'] + 1
            yield scrapy.Request(
                url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': 'Page ' + str(page_num),
                    'page_num': page_num
                },
                callback=self.parse_for_pages
            )

    def extract_links(self, response):
        rows = response.css("tr.cbResultSetDataRow")
        for row in rows:
            url = row.css("a.cbResultSetDataLink::attr(href)").extract_first()
            anchor = " ".join(row.css(" ::text").extract()[:6])

            yield (url, anchor)
