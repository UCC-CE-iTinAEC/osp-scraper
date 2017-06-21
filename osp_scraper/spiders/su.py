# -*- coding: utf-8 -*-

import json

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SUSpider(CustomSpider):
    name = "su"

    start_urls = ["https://sisu.it.su.se/en/educations/search.json"]

    def parse(self, response):
        for item in self.parse_for_urls(response):
            yield item

        jsonresponse = json.loads(response.body_as_unicode())
        for page in range(2, jsonresponse['total_pages'] + 1):
            yield scrapy.FormRequest(
                self.start_urls[0],
                method="GET",
                formdata={
                    'pg': str(page)
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_anchor': "Page " + str(page)
                },
                callback=self.parse_for_urls
            )

    def parse_for_urls(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        for result in jsonresponse['results']:
            rel_url = result['url']
            anchor = " ".join([
                response.meta.get('source_anchor', "Page 1"),
                result['code'],
                result['semester'],
                result['subject'],
                result['name']
            ])

            yield response.follow(
                rel_url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        a_tags = response.css("#course-plan-container a")
        for a_tag in a_tags:
            url = a_tag.css("::attr(href)").get()
            anchor = " ".join([
                response.meta['source_anchor'],
                response.css("h1.course-title::text").get(),
                *a_tag.css("::text").getall()
            ])

            yield (url, anchor)
