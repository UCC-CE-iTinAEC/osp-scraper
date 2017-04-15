# -*- coding: utf-8 -*-

import json
import re

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SFUSpider(CustomSpider):
    name = "sfu"

    start_urls = ["http://www.sfu.ca/outlines.html"]

    def parse(self, response):
        search_url = "http://www.sfu.ca/bin/wcm/course-outlines"
        years = response.css("#year option::attr(value)").extract()

        for year in years:
            url = search_url + "?year=" + year
            yield scrapy.Request(url, callback=self.parse_for_terms)

    def parse_for_terms(self, response):
        for term in json.loads(response.body):
            url = response.url + "&term=" + term["value"]
            yield scrapy.Request(url, callback=self.parse_for_departments)

    def parse_for_departments(self, response):
        for department in json.loads(response.body):
            url = response.url + "&dept=" + department["value"]
            yield scrapy.Request(url, callback=self.parse_for_courses)

    def parse_for_courses(self, response):
        for course in json.loads(response.body):
            url = response.url + "&number=" + course["value"]
            yield scrapy.Request(
                url,
                meta={
                    "anchor": course["title"]
                },
                callback=self.parse_for_sections
            )

    def parse_for_sections(self, response):
        # Get the url parameter values from the request url
        url_params = re.sub(r"[^&]*=", "", response.url).split("&")
        base_url_format = "http://www.sfu.ca/outlines.html?{0}/{1}/{2}/{3}"
        base_url = base_url_format.format(*url_params)

        for section in json.loads(response.body):
            url = base_url + "/" + section["value"]
            yield scrapy.Request(
                url,
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': self.start_urls[0],
                    'source_anchor': response.meta['anchor']
                },
                callback=self.parse_for_files
            )
