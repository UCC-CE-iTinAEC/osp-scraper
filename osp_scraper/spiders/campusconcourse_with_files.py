# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class CampusConcourseWithFilesSpider(CustomSpider):
    name = "campusconcourse_with_files"

    def start_requests(self):
        for start_url in self.start_urls:
            yield scrapy.FormRequest(
                start_url,
                formdata={
                    'search_performed': "1"
                },
                method="GET",
                callback=self.parse_for_pages
            )

    def parse_for_pages(self, response):
        pages_text = response.css(".panel-footer label::text").extract_first()
        num_pages = int(pages_text.split()[-1])

        for page in range(num_pages):
            yield scrapy.FormRequest(
                response.url,
                formdata={
                    'search_performed': "1",
                    'offset': str(page)
                },
                method="GET",
                meta={
                    'source_url': response.url,
                    'source_anchor': "Search Page " + str(page),
                    'depth': 1,
                    'hops_from_seed': 1
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        for row in response.css("#results_table tr"):
            relative_url = row.css("button::attr(onclick)")\
                .re_first(r"get_file\?file_id=[0-9]*")
            if relative_url:
                url = response.urljoin(relative_url)
                anchor = row.css("h4 a::text").extract_first()
                yield (url, anchor)
