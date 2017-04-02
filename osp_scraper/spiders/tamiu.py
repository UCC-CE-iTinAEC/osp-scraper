# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TAMIUSpider(CustomSpider):
    name = "tamiu"

    start_urls = ["https://info.tamiu.edu/courseslist.aspx"]

    def parse(self, response):
        terms = response.css('#ctl00_ContentPlaceHolderMaster_ddlTerms option')
        for term in terms:
            value = term.css('option::attr(value)').extract_first()
            anchor = term.css('option::text').extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    'ctl00$ContentPlaceHolderMaster$ddlTerms': value
                },
                method='POST',
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'termID': value
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        rows = response.css('div#page-wrap tbody tr')
        for row in rows:
            courseID = row.css('td:nth-child(2)::text').extract_first()
            course_section = row.css('td:first-child::text').extract_first()
            # course_sections look like 'COMM 1315.W01'. The part that comes
            # after the period is what's necessary for the syllabus url.
            sectionID = course_section.split('.')[-1]
            relative_url_format = "viewfile.aspx?termID={0}&courseID={1}&sectionID={2}"
            relative_url = relative_url_format.format(
                    response.meta['termID'], courseID, sectionID)
            url = response.urljoin(relative_url)
            anchor = course_section + ' ' + courseID
            yield (url, anchor)
