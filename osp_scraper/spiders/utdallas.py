# -*- coding: utf-8 -*-

import itertools

import scrapy

from ..spiders.CustomSpider import CustomSpider

class UTDallasSpider(CustomSpider):
    """
    Note that it is possible to search all courses and to search by term, but
    results are limited to 300 entries, so the scraper searches by term and by
    course prefix to get around this limitation.
    """

    name = "utdallas"

    start_urls = ["https://coursebook.utdallas.edu/advancedsearch"]

    def parse(self, response):
        url_format = "https://coursebook.utdallas.edu/{0}/{1}/hassyllabus_1?"
        terms = response\
            .css(".selectlist-block:nth-child(2) select option::attr(value)")\
            .extract()
        prefixes = response\
            .css(".selectlist-block:nth-child(3) select option::attr(value)")\
            .extract()
        for term, prefix in itertools.product(terms, prefixes):
            url = url_format.format(term, prefix)
            yield scrapy.Request(url, callback=self.parse_for_courses)

    def parse_for_courses(self, response):
        for row in response.css("tbody tr"):
            # Get the course ID from the fourth argument to open_subrow in
            # the onclick attribute of the row. The course_id looks like:
            # acct2301.002.17s
            course_id = row.css("tr::attr(onclick)")\
                .re_first(r"open_subrow\(.*?,.*?,.*?, '(.*?)'")
            course_name = row.css("td:nth-child(3)::text").extract_first()

            yield scrapy.FormRequest(
                "https://coursebook.utdallas.edu/clips/clip-coursebook-overview.zog",
                method="POST",
                formdata={
                    'id': course_id,
                    'div': "r-1childcontent",
                    'subaction': "null"
                },
                meta={
                    'source_anchor': course_id + " " + course_name,
                    'source_url': response.url,
                    'course_id': course_id
                },
                callback=self.parse_for_syllabus_clip_url
            )

    def parse_for_syllabus_clip_url(self, response):
        yield scrapy.FormRequest(
            "https://coursebook.utdallas.edu/clips/clip-syllabus.zog",
            method="POST",
            formdata={
                'id': response.meta['course_id'],
                'div': "r-1childcontent",
                'action': "syllabus"
            },
            meta={
                'depth': 2,
                'hops_from_seed': 2,
                'source_url': response.meta['source_url'],
                'source_anchor': response.meta['source_anchor']
            },
            callback=self.parse_for_files
        )

    def extract_links(self, response):
        url = response.css(".expandblock-content a::attr(href)").extract_first()
        anchor = response.meta['source_anchor']
        yield (url, anchor)
