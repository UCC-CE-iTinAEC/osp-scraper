# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy

from ..spiders.CustomSpider import CustomSpider

class CityUSpider(CustomSpider):
    """
    This site uses javascript to embed "catalogue pages", which contain all the
    interesting links, inside the pages which you normally navigate on.
    However, we can't use the catalogue pages on their own, since all those
    links are relative links that only work with the URLs of the normal pages,
    so some maneuvering is required.
    """
    name = "cityu"

    start_urls = [
        "http://www.cityu.edu.hk/pg/201617/catalogue/R/R_course_index.htm"
    ]

    base_url = "http://www.cityu.edu.hk/pg/201617/catalogue/catalogue_R.htm"

    def parse(self, response):
        a_tags = response.css("a")
        for a_tag in a_tags:
            rel_url = a_tag.css("::attr(href)").get().split("/")[-1]
            anchor = a_tag.css("::text").get()
            yield response.follow(
                rel_url,
                meta={
                    'anchor': anchor
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        a_tags = response.css("a")
        for a_tag in a_tags:
            rel_url = a_tag.css("::attr(href)").get()
            anchor = a_tag.css("::text").get()
            yield scrapy.Request(
                urljoin(self.base_url, rel_url),
                meta={
                    'anchor': response.meta['anchor'] + " " + anchor
                },
                callback=self.parse_for_syllabi
            )

    def parse_for_syllabi(self, response):
        # NOTE: The more natural approach might be to implement `extract_links`,
        # but that approach downloads both the source page and the link, and
        # both are syllabi-like, so it might be a good idea to avoid the
        # possibility of duplication.
        link = response.css("#pdf_url::text").get()
        # NOTE: Should we download the course page if the syllabus link isn't
        # available?
        if link:
            yield response.follow(
                link,
                meta={
                    'depth': 3,
                    'hops_from_seed': 3,
                    'source_url': response.url,
                    'source_anchor': response.meta['anchor']
                },
                callback=self.parse_for_files
            )
