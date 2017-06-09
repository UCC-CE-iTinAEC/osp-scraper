# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class KUSpider(CustomSpider):
    name = "ku"

    # TODO: Find shorter URL?
    start_urls = [
        # The 'IdLanguage=133" means results are in English, or as much English
        # as is made available -- sometimes of the syllabi are still in German.
        "https://campus.ku.de/studienangebot/evt_pages/SuchResultat.aspx?node=d175b8fe-7eca-4c19-b50b-7534643c201a&TabKey=WebTab_CstPI2_ModuleAZ&IdLanguage=133"
    ]

    def parse(self, response):
        sems = response.css("#ctl00_WebPartManager1_SuchregisterWP1_DropDownList4")\
            .css("option::attr(value)").getall()
        for sem in sems[1:]:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'ctl00$WebPartManager1$SuchregisterWP1$DropDownList4': sem,
                    'ctl00$WebPartManager1$SuchregisterWP1$ctl09': "Search"
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': sem + " Page$First",
                    'sem': sem
                },
                callback=self.parse_for_pages
            )

    def parse_for_pages(self, response):
        for item in self.parse_for_syllabi(response):
            yield item

        next_page_num = str(response.meta['hops_from_seed'] + 1)
        eventargument = "Page$" + next_page_num

        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            formdata={
                '__EVENTTARGET':
                    "ctl00$WebPartManager1$ResultatAnzeigenWP1$ctl01",
                '__EVENTARGUMENT': eventargument,
                # This key would normally hold "Search", but we don't want
                # to execute a new search on page iteration.
                'ctl00$WebPartManager1$SuchregisterWP1$ctl09': None
            },
            meta={
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
                'source_url': response.url,
                'source_anchor': response.meta['sem'] + " " + eventargument,
                'sem': response.meta['sem']
            },
            callback=self.parse_for_pages
        )

    def parse_for_syllabi(self, response):
        rows = response.css("#ctl00_WebPartManager1_ResultatAnzeigenWP1_ctl01")\
            .css("tr.result-row")
        for row in rows:
            url = row.css("td:first-child a:last-child::attr(href)").get()
            anchor = " ".join([
                response.meta['source_anchor'],
                *row.css("td ::text").getall()[:3]
            ])
            yield response.follow(
                url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
