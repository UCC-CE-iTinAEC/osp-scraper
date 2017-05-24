# -*- coding: utf-8 -*-

import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class UTASpider(CustomSpider):
    """
    All of the syllabus files are behind redirects, so this scraper requests
    the file directly instead of using the file pipeline.
    """
    name = "uta"

    start_urls = ["https://mentis.uta.edu/explore/courses/all"]

    def parse(self, response):
        num_results = int(response.css("#search-message strong::text").get())
        num_pages = (num_results+9)//10 # Divide by the page size, rounded up

        for page in range(1, num_pages+1):
            yield scrapy.FormRequest(
                response.url,
                headers={
                    "x-requested-with": "XMLHttpRequest"
                },
                formdata={
                    'keyword': "",
                    'page': str(page)
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        html = json.loads(response.body)["courseResultCards"]
        sel = scrapy.Selector(text=html, type="html")
        courses = sel.css(".result-card")
        for course in courses:
            url = course.css(".syllabus::attr(href)")\
                .re_first(r"/dashboard/file/download/id/[0-9]+")
            if url:
                anchor = " ".join([
                    *course.css(".title ::text").getall(),
                    *course.css(".semester-year ::text").getall()
                ])
                yield response.follow(
                    url,
                    meta={
                        'depth': 2,
                        'hops_from_seed': 2,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )
