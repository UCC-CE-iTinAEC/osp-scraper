# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SnowSpider(CustomSpider):
    name = "snow"

    start_urls = ["https://www.snow.edu/syllabus/?action=search&subject=normal"]

    def start_requests(self):
        for request in super().start_requests():
            request.meta['source_url'] = request.url
            request.meta['source_anchor'] = '1'
            yield request

    def parse(self, response):
        for item in self.parse_for_files(response):
            yield item

        page_tags = response.css("table tr:nth-child(2) td a")
        # Check to see if there's a 'Next' anywhere in the tags list.
        if page_tags.re_first(r"Next"):
            # The 'href' attribute of each link looks like:
            # javascript:searchPage(<page number>)
            next_page_num = page_tags.css("::attr(href)")[-1].re(r"\((\d+)\)")[0]
            yield scrapy.FormRequest(
                "https://www.snow.edu/syllabus/",
                method="GET",
                formdata={
                    'action': "search",
                    'subject': "normal",
                    'page': next_page_num
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': next_page_num
                },
                callback=self.parse
            )

    def extract_links(self, response):
        tags = response.css("tr td.list a")
        for tag in tags:
            # The 'href' attribute of each tag looks like:
            # javascript:newaction('<action>','<subject>','<indexX>','<indexY>')
            # The 'action' seems like it can always be 'viewSyllabus', and
            # 'indexX' and 'indexY' seem like they are always the empty string
            # and not relevant for getting the syllabi either.
            subject = tag.css("::attr(href)").re(r"'(.*?)'")[1]
            url = "https://www.snow.edu/syllabus/?action=viewSyllabus&subject={}"
            url = url.format(subject)
            anchor = tag.css("::text").extract_first()

            yield (url, anchor)
