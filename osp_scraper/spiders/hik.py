# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class HIKSpider(CustomSpider):
    name = "hik"

    start_urls = [
        "http://utbildning.hik.se/ShowCourses.aspx?ShowSyllSv=True&ShowSyllEn=True&Lang=En"
    ]

    def parse(self, response):
        cur_page = response.css("#logPageLinksTable span.publastline ::text")\
                           .get()
        response.meta['source_url'] = response.url
        response.meta['source_anchor'] = 'Page ' + cur_page

        for item in self.parse_for_files(response):
            yield item

        # NOTE: It would be nice to loop and yield all the pages at once, but
        # that seems difficult to accomplish with this site -- not all pages are
        # available on the first page, hrefs for pages change as pages are
        # iterated and `from_response` doesn't seem to work nicely.  Using
        # `from_response` with the next page button, however, is quite
        # convenient.
        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            formdata={
                'logNextpage': '>>'
            },
            meta={
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1
            },
            callback=self.parse
        )

    def extract_links(self, response):
        rows = response.css("td.publink3")
        for row in rows:
            # Want to grab the English syllabus if it is available, defaulting
            # to the Swedish syllabus if it is not.
            a_tag = row.css("a.publastline[href$='Lang=En']")
            if not a_tag:
                a_tag = row.css("a.publastline")

            rel_url = a_tag.css("::attr(href)").get()
            anchor = " ".join([
                response.meta['source_anchor'],
                row.css("a.publink3::text").get(),
                a_tag.css("::text").get()
            ])

            yield (rel_url, anchor)
