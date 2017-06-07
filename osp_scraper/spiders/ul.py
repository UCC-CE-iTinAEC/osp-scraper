# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ULSpider(CustomSpider):
    '''
    This site is a bit odd: all search results appear as text embedded
    underneath the search field entry, and need to be iterated through one at a
    time with POST requests to the next button.  Thankfully, it seems like all
    syllabi can be scraped in a single search.
    '''
    name = "ul"

    start_urls = ["https://bookofmodules.ul.ie/"]

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            # As far as I can tell, `formdata` values don't matter, as long as
            # they're numbers and are present.
            formdata={
                'ctl00$MasterContentPlaceHolder$SubmitQuery.x': '1',
                'ctl00$MasterContentPlaceHolder$SubmitQuery.y': '1'
            },
            meta={
                'depth': 1,
                'hops_from_seed': 1,
                'source_url': response.url
            },
            callback=self.parse_for_pages
        )

    def parse_for_pages(self, response):
        # The course title seems to be the most sensible choice of anchor, but
        # is only available after the page has been loaded.
        anchor = " ".join(
            response.css(".NoticeStyle + .ModuleLayoutStyle::text").getall()
        )
        response.meta['source_anchor'] = anchor
        for item in self.parse_for_files(response):
            yield item

        current_page = response.css("#ctl00_MasterContentPlaceHolder_ModuleFull_ListViewDataPager_ctl01_CurrentPageLabel::text")\
                               .get()
        total_pages = response.css("#ctl00_MasterContentPlaceHolder_ModuleFull_ListViewDataPager_ctl01_TotalPagesLabel::text")\
                              .get()
        if int(current_page) == int(total_pages):
            return

        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            # Same deal with this `formdata` as with the request in `parse`.
            formdata={
                'ctl00$MasterContentPlaceHolder$ModuleFull_ListViewDataPager$ctl00$ctl02.x':
                    '1',
                'ctl00$MasterContentPlaceHolder$ModuleFull_ListViewDataPager$ctl00$ctl02.y':
                    '1'
            },
            meta={
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
                'source_url': response.url
            },
            callback=self.parse_for_pages
        )
