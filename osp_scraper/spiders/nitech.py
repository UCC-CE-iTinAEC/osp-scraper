# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class NITECHSpider(CustomSpider):
    name = "nitech"

    start_urls = ["http://syllabus.ict.nitech.ac.jp/search_eng.php"]

    def parse(self, response):
        years = response.css("select[name='sea_nendo'] option::attr(value)")\
                        .getall()
        for year in years:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'sea_nendo': year
                },
                meta={
                    'anchor': year + ' Page 1'
                },
                callback=self.parse_for_pages
            )

    def parse_for_pages(self, response):
        for item in self.parse_for_syllabi(response):
            yield item

        # href element looks like this:
        #   JavaScript:course_custom_paging(<page number>)
        total_pages = response.css("div.paging a:nth-last-child(2)::attr(href)")\
                              .re_first("\d+")
        # Some search results are only a single page.
        if not total_pages:
            return

        for page_num in range(1, int(total_pages)):
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'page': str(page_num)
                },
                meta={
                    'anchor': response.meta['anchor'] + ' Page ' + str(page_num)
                },
                callback=self.parse_for_syllabi
            )

    def parse_for_syllabi(self, response):
        rows = response.css("table[width='80%'] tr")
        for row in rows[1:]:
            a_tag = row.css("td:nth-child(4) a")[0]
            row_text = row.css(" ::text").getall()
            anchor = " ".join([
                response.meta['anchor'],
                *row_text[:5],
                *row_text[8:]
            ])

            yield response.follow(
                a_tag,
                meta={
                    'depth': 3,
                    'hops_from_seed': 3,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
