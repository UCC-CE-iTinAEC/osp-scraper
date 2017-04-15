# -*- coding: utf-8 -*-

import scrapy
import json

from ..spiders.CustomSpider import CustomSpider

class WesternSeminarySpider(CustomSpider):
    name = "westernseminary"

    def start_requests(self):
        start_url = "https://www.westernseminary.edu/api/ws-syllabi.php?getcampusdata=1"
        search_url = "https://www.westernseminary.edu/api/ws-syllabi.php?getsyllabi=1&cmp={0}&sem={1}"

        def get_parameters(response):
            campuses = json.loads(response.body)
            for cid in campuses:
                semesters = campuses[cid]["semesters"]
                for semester in semesters:
                    url = search_url.format(cid, semester.replace(" ", "+"))
                    anchor = campuses[cid]["name"] + " " + semester
                    yield scrapy.Request(
                        url,
                        meta={
                            "depth": 1,
                            "hops_from_seed": 1,
                            "source_url": response.url,
                            "source_anchor": anchor
                        },
                        callback=self.parse_for_files
                    )

        yield scrapy.Request(start_url, callback=get_parameters)

    def extract_links(self, response):
        results = json.loads(response.body)
        for result in results:
            url = result['url']
            name = result['crsname']
            yield (url, name)
