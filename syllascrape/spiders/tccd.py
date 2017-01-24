
# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TCCDSpider(CustomSpider):
    name = "tccd"
    allowed_domains = ["tccd.edu"]

    def start_requests(self):
        start_url_format = "https://waj.tccd.edu/TCC/Courses/ugCourses{0}.jsp"

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            url = start_url_format.format(letter)
            yield scrapy.Request(url, callback=self.parse_directory_page)

    def parse_directory_page(self, response):
        for tag in response.css("#courseLists a"):
            url = tag.css("a::attr(href)").extract_first()
            anchor = tag.css("a::text").extract_first()

            yield scrapy.Request(
                url, 
                meta={
                    "depth": 1,
                    "hops_from_seed": 1,
                    "source_url": response.url,
                    "source_anchor": anchor,
                },
                callback=self.parse_for_files
            )

    def get_file_links(self, response):
        syllabus_link_tag = response.css('tr:last-child td.info a')
        syllabus_relative_url = syllabus_link_tag.css('a::attr(href)').re_first("displayLink[^']*")
        url = response.urljoin(syllabus_relative_url)
        anchor = syllabus_link_tag.css('a::text').extract_first()

        yield (url, anchor)