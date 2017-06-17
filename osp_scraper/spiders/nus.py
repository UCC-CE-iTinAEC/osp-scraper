# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class NUSSpider(CustomSpider):
    name = "nus"

    start_urls = ["https://ivle.nus.edu.sg/lms/public/list_course_public.aspx"]

    def parse(self, response):
        # Need to iterate through pages, but first scrape the landing page.
        for item in self.parse_for_syllabi(response):
            yield item

        pages = response.css("#GV_Page2 option")
        for page in pages[1:]:
            page_value = page.css("::attr(value)").get()
            page_text = page.css("::text").get()

            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    '__EVENTTARGET': "ctl00$ContentPlaceHolder1$GV",
                    '__EVENTARGUMENT': 'pg2',
                    'GV_Page2': page_value,
                    'ctl00$ContentPlaceHolder1$btnSearch': None
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_anchor': "Page " + page_text
                },
                callback=self.parse_for_syllabi
            )

    def parse_for_syllabi(self, response):
        rows = response.css("#ctl00_ContentPlaceHolder1_GV tr")
        for row in rows[1:]:
            # onclick elements look like this:
            #   winopen('<relative url>',0,0);return false;
            onclick = row.css("td:first-child a::attr(onclick)").get()
            if onclick:
                relative_url = onclick.split("'")[1]

                page_text = response.meta.get('source_anchor', 'Page 1')
                row_text = " ".join(row.css("td ::text").getall()[:-2])

                yield response.follow(
                    relative_url,
                    meta={
                        'depth': response.meta['depth'] + 1,
                        'hops_from_seed': response.meta['hops_from_seed'] + 1,
                        'source_url': response.url,
                        'source_anchor': page_text + " " + row_text
                    },
                    callback=self.parse_for_files
                )
