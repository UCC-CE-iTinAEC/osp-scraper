# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class BHSECSpider(CustomSpider):
    name = "bhsec"

    start_urls = [
        "http://bhsec.bard.edu/manhattan/academics/courses/",
        "http://bhsec.bard.edu/queens/academics/courses/"
    ]

    def parse(self, response):
        options = response.css("select option")
        for option in options:
            course_id = option.css("::attr(value)").extract_first()
            course_name = option.css("::text").extract_first()
            url = response.url + "courses.php?listing_id=" + course_id
            yield scrapy.Request(
                url,
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': course_name
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        for a_tag in response.css("a"):
            href = a_tag.css("::attr(href)").extract_first()
            if "getfile" in href:
                anchor = a_tag.css("::text").extract_first()
                yield (href, anchor)
