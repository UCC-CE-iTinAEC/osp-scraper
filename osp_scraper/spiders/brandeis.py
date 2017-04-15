# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class BrandeisSpider(CustomSpider):
    name = "brandeis"
    allowed_domains = ["brandeis.edu"]

    def start_requests(self):
        # Trying to do searches starting from
        # "http://registrar-prod.unet.brandeis.edu/registrar/schedule/search/"
        # breaks for some reason.
        start_url = "http://registrar-prod.unet.brandeis.edu/registrar/schedule/search/2017/Spring/1171/search"

        def get_terms(response):
            terms = response.css("select[name='strm'] option")
            for term in terms:
                code = term.css("option::attr(value)").extract_first()
                anchor = term.css("option::text").extract_first()
                # The anchor contains CRLF newlines, so clean it up.
                anchor = " ".join(anchor.split())
                yield scrapy.FormRequest.from_response(
                    response,
                    method="GET",
                    formdata={
                        'strm': code
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': anchor
                    },
                    callback=get_pages
                )

        def get_pages(response):
            # Entering a search lands us on page 1 of of the results, so parse
            # it immediately.
            for item in self.parse_for_files(response):
                yield item
            # There's a row for page numbers on both the top and the bottom, so
            # just take the top one.
            pages = response.css("div.paging")[0]
            # Last entry is a 'Next' symbol, so ignore it.
            page_numbers = pages.css("a::text").extract()[:-1]
            for number in page_numbers:
                anchor = response.meta['source_anchor'] + " " + number
                yield scrapy.FormRequest.from_response(
                    response,
                    method="GET",
                    formdata={
                        'page': number
                    },
                    meta={
                        'depth': response.meta['depth'] + 1,
                        'hops_from_seed': response.meta['hops_from_seed'] + 1,
                        'source_url': response.url,
                        # Use current page number as part of the anchor.
                        'source_anchor': anchor
                    },
                    callback=self.parse_for_files
                )


        yield scrapy.Request(start_url, callback=get_terms)

    def extract_links(self, response):
        # First row is the table header, so ignore it.
        table_rows = response.css("table#classes-list tr")[1:]
        for row in table_rows:
            url = row.css("td:nth-child(2) a[target='_blank']::attr(href)")\
                .extract_first()
            # Some table rows don't contain links to syllabi, so check for that
            # possibility and skip this iteration if so.
            if not url:
                continue
            anchor = row.css("td:nth-child(2) a.def::text").extract_first()
            # The anchor contains CRLF newlines (again), so clean it up.
            anchor = " ".join(anchor.split())
            yield (url, anchor)
