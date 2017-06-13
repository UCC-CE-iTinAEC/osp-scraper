# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ICUSpider(CustomSpider):
    name = "icu"

    start_urls = [
        "https://campus.icu.ac.jp/public/ehandbook/SearchCourseAndSyllabus.aspx?lang=e"
    ]

    def parse(self, response):
        years = response.css("#ctl00_ContentPlaceHolder1_ddl_year_e")\
                        .css("option::attr(value)").getall()
        for year in years:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'ctl00$ContentPlaceHolder1$ddl_year_e': year,
                    # '0' here means all terms.
                    'ctl00$ContentPlaceHolder1$ddl_term_e': "0",
                    'ctl00$ContentPlaceHolder1$ddl_major_e': "",
                    'ctl00$ContentPlaceHolder1$btn_search_e': "GO"
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': year + " Page$1",
                    'year': year,
                    'page': 1
                },
                callback=self.parse_for_pages
            )

    def parse_for_pages(self, response):
        for item in self.parse_for_files(response):
            yield item

        page = response.meta['page'] + 1
        eventargument = "Page$" + str(page)

        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            formdata={
                '__EVENTTARGET': "ctl00$ContentPlaceHolder1$grv_course_e",
                '__EVENTARGUMENT': eventargument,
                'ctl00$ContentPlaceHolder1$btn_search_e': None
            },
            meta={
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
                'source_url': response.url,
                'source_anchor': response.meta['year'] + " " + eventargument,
                'year': response.meta['year'],
                'page': page
            },
            callback=self.parse_for_pages
        )

    def extract_links(self, response):
        # Need to slice off two rows at the beginning (page numbers and header)
        # and one at the end (page numbers).
        rows = response.css("#ctl00_ContentPlaceHolder1_grv_course_e > tr")[2:-1]
        for row in rows:
            rel_url = row.css("a[id$='hpl_syllabus']::attr(href)").get()
            anchor = " ".join([
                response.meta['source_anchor'],
                *row.css("td ::text").getall()
            ])

            yield (rel_url, anchor)
