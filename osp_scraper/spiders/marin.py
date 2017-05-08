# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class MarinSpider(CustomSpider):
    name = "marin"

    start_urls = ["http://www.marin.edu/Apps/Directory/CourseSearch.aspx"]

    def parse(self, response):
        pages = response.css("span.tableTitlex a")
        for page in pages:
            rel_url = page.css("::attr(href)").extract_first()
            url = response.urljoin(rel_url)
            anchor = page.css("::text").extract_first()

            yield scrapy.Request(
                url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        syllabi_url = "http://www.marin.edu/Apps/Directory/CourseInfo.aspx?ID={0}"
        rows = response.css("#MainContent_grdCourse tr")
        for row in rows[1:]:
            # The 'href' attributes look like this:
            # Javascript:openCourseInfo('<code>');
            code = row.css("td:first-child a::attr(href)").re_first(r"'(\d+)'")
            url = syllabi_url.format(code)
            anchor = " ".join(row.css("td ::text").extract())

            yield (url, anchor)
