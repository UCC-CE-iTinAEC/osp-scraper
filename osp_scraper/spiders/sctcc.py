# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SCTCCSpider(CustomSpider):
    name = "sctcc"

    start_urls = ["https://webproc.mnscu.edu/registration/viewCourseOutlines.do?campusid=208"]

    def parse(self, response):
        sem_values   = response.css("#selectedYearTerm option::attr(value)")\
                               .extract()
        sem_anchors  = response.css("#selectedYearTerm option::text")\
                               .extract()
        subj_values  = response.css("#selectedSubject option::attr(value)")\
                               .extract()
        subj_anchors = response.css("#selectedSubject option::text")\
                               .extract()

        for sem_value, sem_anchor in zip(sem_values, sem_anchors):
            for subj_value, subj_anchor in zip(subj_values, subj_anchors):
                yield scrapy.FormRequest(
                    "https://webproc.mnscu.edu/registration/viewCourseOutlines.do",
                    formdata={
                        'selectedYearTerm': sem_value,
                        'selectedSubject': subj_value
                    },
                    method="POST",
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': sem_anchor + ' ' + subj_anchor,
                        'require_files': True
                    },
                    callback=self.parse_for_files
                )

    def extract_links(self, response):
        results = response.css("#searchResults tr td:last-child a")
        for result in results:
            rel_url = result.css("a::attr(href)").extract_first()
            url = response.urljoin(rel_url)
            anchor = result.css("a::attr(title)").extract_first()
            yield (url, anchor)
