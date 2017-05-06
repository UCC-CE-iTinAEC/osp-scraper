# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class CharterOakSpider(CustomSpider):
    name = "charteroak"

    start_urls = ["https://www.charteroak.edu/syllabus/"]

    def parse(self, response):
        disciplines = response.css("#menu1 option")
        for disc in disciplines[1:]:
            rel_url = disc.css("::attr(value)").extract_first()
            anchor = disc.css("::text").extract_first()
            yield scrapy.Request(
                response.urljoin(rel_url),
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        tags = response.css("a")
        for tag in tags:
            # The 'a' tag 'onclick' attributes look like this:
            # return popitup('<url>');
            url = tag.css("::attr(onclick)").re_first(r"'(.*?)'")

            # NOTE: There are occasionally additional links on the pages, ones
            # that don't pass this check.  Follow/download those as well?
            if url:
                # All the links are http but redirect to https versions, so save
                # time by just changing the string.
                url = url.replace("http://", "https://")
                anchor = tag.css("::text").extract_first()
                yield (url, anchor)
