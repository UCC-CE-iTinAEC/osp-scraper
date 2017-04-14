# -*- coding: utf-8 -*-

import scrapy
import json

from ..spiders.CustomSpider import CustomSpider

class CMichSpider(CustomSpider):
    name = "cmich"

    def start_requests(self):
        start_url = "https://globalapp.cmich.edu/PublicWeb/API/ScheduledCourses/Schedules?day=SU,MO,TU,WE,TH,FR,SA"

        yield scrapy.Request(
            start_url,
            headers={
                'Accept' : "application/json"
            },
            meta={
                'source_url': start_url,
                'source_anchor': "",
                'depth': 1,
                'hops_from_seed': 1
            },
            callback=self.parse_for_files
        )

    def extract_links(self, response):
        for course in json.loads(response.body):
            crn = course.get('Crn')
            anchor = course.get('CourseTitle')
            if crn and anchor:
                url = "https://sbt.globalapp.cmich.edu/public/PublicSyllabusViewer.aspx?EPN=" + crn
                yield (url, anchor)
