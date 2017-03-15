# -*- coding: utf-8 -*-

import json
import scrapy

from ..spiders.CustomSpider import CustomSpider

class MHCSpider(CustomSpider):
    name = "mhc"
    allowed_domains = ["mhc.ab.ca"]

    def start_requests(self):
        api_url = "http://courseoutlines.mhc.ab.ca/pcom/api/Outlines/GetOutlinesWithPaging"

        def get_pdfs(response):
            api_url = "http://courseoutlines.mhc.ab.ca/pcom/api/Outlines/GetOutlinePdf"
            jsonresponse = json.loads(response.body_as_unicode())
            for entry in jsonresponse['data']:
                num = entry['Id']
                # Set the anchor to something more useful.
                anchor = entry['CourseCode']
                yield scrapy.FormRequest(
                    api_url,
                    formdata={
                        'outlineId': str(num),
                    },
                    meta={
                        'source_url': response.url,
                        'source_anchor': anchor,
                        'depth': 1,
                        'hops_from_seed': 1,
                    },
                    method='GET',
                    callback=self.parse_for_files
                )

        yield scrapy.FormRequest(
            api_url,
            formdata={
                'start': '1',
                # Set limit to -1 to signify no limit and pull all courses.
                'limit': '-1',
            },
            method='GET',
            callback=get_pdfs
        )
