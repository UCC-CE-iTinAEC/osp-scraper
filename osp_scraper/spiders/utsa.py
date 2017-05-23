# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class UTSASpider(CustomSpider):
    name = "utsa"

    start_urls = ["https://bluebook.utsa.edu/"]

    def parse(self, response):
        subjs = response\
            .css("#ctl00_MainContentSearchQuery_searchCriteriaEntry_CourseSubjectCombo_OptionList ")\
            .css("li::text")\
            .getall()

        for hidden_value, subj in enumerate(subjs, 1):
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    '__EVENTTARGET':
                        "ctl00$MainContentSearchQuery$searchCriteriaEntry$SearchBtn",
                    'ctl00$MainContentSearchQuery$searchCriteriaEntry$CourseSubjectCombo$TextBox':
                        subj,
                    'ctl00$MainContentSearchQuery$searchCriteriaEntry$CourseSubjectCombo$HiddenField':
                        str(hidden_value),
                    'ctl00$HeaderBtnCntrl$HomeBtn': None
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': subj + " Page 1",
                    'require_files': True,
                    'subj': subj
                },
                callback=self.parse_for_pages
            )

    def parse_for_pages(self, response):
        for item in self.parse_for_files(response):
            yield item

        main_table = response\
            .css("#ctl00_MainContent_mainContent1_AccordionRndPanel")
        # The next page button is always present, but if on the final page, it
        # is given the "disabled" attribute.
        next_page_button_disabled = response\
            .css("#ctl00_MainContent_mainContent1_PagerImgBtn_NextTOP")\
            .css("::attr(disabled)")

        if main_table and not next_page_button_disabled:
            page_num = response.css("#ctl00_MainContent_mainContent1_topPagerPnl")\
                               .css("div:nth-child(2)::text")\
                               .get().split()[0]

            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                # While it seems like these entries in formdata are necessary to
                # simulate a press of the next page button, it doesn't seem like
                # the actual values matter.
                formdata={
                    'ctl00$MainContent$mainContent1$PagerImgBtn_NextTOP.x': "1",
                    'ctl00$MainContent$mainContent1$PagerImgBtn_NextTOP.y': "1"
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['depth'] + 1,
                    'source_url': response.url,
                    'source_anchor': response.meta['subj'] + " Page " + page_num,
                    'require_files': True,
                    'subj': response.meta['subj']
                },
                callback=self.parse_for_pages
            )

    def extract_links(self, response):
        rows = response.css("table.infoTable tr")
        for row in rows:
            anchor = " ".join(row.css("td")[:4].css("::text").getall())

            # Links to textbooks have onclick attributes that look like this:
            #   window.open('<url>'); return false;
            book_url = row.css("td:nth-child(7) a::attr(onclick)").get()
            if book_url:
                book_url = book_url.split("'")[1]
                yield (book_url, anchor + " Books")

            # Links to syllabi have onclick attributes that look like this:
            #   javascript:window.open('<relative-url>'); return false;
            syllabus_url = row.css("td:nth-child(8) a::attr(onclick)").get()
            if syllabus_url:
                syllabus_url = syllabus_url.split("'")[1]
                yield (syllabus_url, anchor + " Syllabus")
