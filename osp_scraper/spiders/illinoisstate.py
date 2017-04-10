# -*- coding: utf-8 -*-

import itertools
import scrapy

from ..spiders.CustomSpider import CustomSpider

class IllinoisStateSpider(CustomSpider):
    name = "illinoisstate"
    allowed_domains = ["illinoisstate.edu"]

    def start_requests(self):
        database_url = "https://casit.illinoisstate.edu/syllabi/Database/QuerySelect"
        archive_url = "https://casit.illinoisstate.edu/syllabi/Archive/QuerySelect"

        def get_database_searches(response):
            depts = response.css('#Department option::attr(value)').extract()
            sems = response.css('#semester option::attr(value)').extract()
            years = response.css('#year option::attr(value)').extract()
            for dept, sem, year in itertools.product(depts, sems, years):
                yield scrapy.FormRequest(
                    'https://casit.illinoisstate.edu/syllabi/Database/QueryResults',
                    formdata={
                        'Department': dept,
                        'semester': sem,
                        'year': year,
                    },
                    method='POST',
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': ' '.join([dept, sem, year]),
                    },
                    callback=self.parse_for_files
                )

        def get_archive_searches(response):
            depts = response.css('#deptNum option::attr(value)').extract()
            sems = response.css('#semester option::attr(value)').extract()
            years = response.css('#year option::attr(value)').extract()
            for dept, sem, year in itertools.product(depts, sems, years):
                yield scrapy.FormRequest(
                    'https://casit.illinoisstate.edu/syllabi/Archive/QueryResults',
                    formdata={
                        'deptNum': dept,
                        'semester': sem,
                        'year': year,
                    },
                    method='GET',
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': ' '.join([dept, sem, year]),
                    },
                    callback=self.parse_for_files
                )

        yield scrapy.Request(database_url, callback=get_database_searches)
        yield scrapy.Request(archive_url, callback=get_archive_searches)

    def extract_links(self, response):
        table_rows = response.css('table#syllabusList tbody tr')
        for row in table_rows:
            url = row.css('tr td:last-child a::attr(href)').extract_first()
            class_num = row.css('tr td:nth-child(3)::text').extract_first()
            section = row.css('tr td:nth-child(4)::text').extract_first()
            anchor = class_num.strip() + ' ' + section
            yield (url, anchor)
