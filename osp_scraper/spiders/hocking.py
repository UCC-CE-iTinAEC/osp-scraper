# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class HockingSpider(CustomSpider):
    name = "hocking"
    allowed_domains = ["hocking.edu"]

    def start_requests(self):
        start_url = "http://www.hocking.edu/academicsupport/courseoutlines/"

        def get_term(response):
            # Skip the first entry since it has no value.
            for term in response.css("select option")[1:]:
                term_code = term.css("option::attr(value)").extract_first()
                anchor = term.css("option::text").extract_first()
                # NOTE: from_response does not work, returns empty results page.
                yield scrapy.FormRequest(
                    start_url,
                    method="POST",
                    formdata={
                        'ddlTerm': term_code,
                        'txtSearch': "",
                        'btnSubmit': "Search"
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )

        yield scrapy.Request(start_url, callback=get_term)

    def extract_links(self, response):
        # Skip the first row because it's the table header.
        for row in response.css("table.styledTable tr")[1:]:
            relative_url = row.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            # Text of each 'a' element is always "View/Save", so use previous
            # columns to construct the anchor.
            term = row.css("td:first-child::text").extract_first()
            course_title = row.css("td:nth-child(2)::text").extract_first()
            course_number = row.css("td:nth-child(3)::text").extract_first()
            anchor = " ".join([term, course_title, course_number])
            yield (url, anchor)
