# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class CedarCrestSpider(CustomSpider):
    name = "cedarcrest"
    allowed_domains = ["cedarcrest.edu"]

    def start_requests(self):
        start_url = "https://my.cedarcrest.edu/ics/staticpages/syllabilist.aspx"

        def get_terms(response):
            terms = response.css("select#ddlTerm option")
            for term in terms:
                value = term.css("option::attr(value)").extract_first()
                anchor = term.css("option::text").extract_first()
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata={
                        'ddlTerm': value,
                        'btnSubmit': "Submit"
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    method='POST',
                    callback=self.parse_for_files
                )

        yield scrapy.Request(start_url, callback=get_terms)

    def extract_links(self, response):
        # Exclude the first result because it's a header.
        table_rows = response.css("table#dgSyllabi tr")[1:]
        for row in table_rows:
            url = row.css("td a::attr(href)").extract_first()
            anchor = row.css("td a::text").extract_first()
            # The anchors can contain a lot of excess whitespace, so clean that
            # up a bit.
            anchor = " ".join(anchor.split())
            yield (url, anchor)
