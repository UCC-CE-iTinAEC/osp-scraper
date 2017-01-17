# -*- coding: utf-8 -*-

import scrapy
from syllascrape.items import PageItem 

class ASUSpider(scrapy.spiders.Spider):
    name = "asu"
    allowed_domains = ["asu.edu"]

    def start_requests(self):
        terms = []
        subjects = []

        start_url = "https://webapp4.asu.edu/catalog/"

        def get_terms_codes(response):
            terms.extend(response.css("#term option::attr(value)").extract())
            return scrapy.Request("https://webapp4.asu.edu/catalog/Subjects.html", callback=get_subject_codes)

        def get_subject_codes(response):
            subjects.extend(response.css(".subject::text").extract())
            return start_form_requests()

        def start_form_requests():
            for term_code in terms:
                for subject_code in subjects:
                    yield scrapy.FormRequest(
                        "https://webapp4.asu.edu/catalog/classlist",
                        formdata={
                            "s": subject_code,
                            "t": term_code,
                            "e": "all",
                            "hon": "F",
                            "promod": "F",
                        },
                        method='GET',
                        cookies={"onlineCampusSelection":"C"},
                        meta={
                            "depth": 1,
                            "hops_from_seed": 1,
                            "source_url": start_url,
                            "source_anchor": "",
                        },
                        callback=self.parse
                    )

        yield scrapy.Request(start_url, callback=get_terms_codes, dont_filter=True)



    def parse(self, response):

        file_urls = []

        syllabi_tags = response.css('a[title="Syllabus"]').extract()
        for tag in syllabi_tags:
            url = tag.css('base::attr(href)')
            anchor = tag.css('base::text')

            meta = {
                'source_url': response.url,
                'source_anchor': anchor,
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
            }

            file_urls.append((url, meta))

        yield PageItem(
            url=response.url,
            content=response.body,
            headers=response.headers,
            status=response.status,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
            depth=response.meta.get('depth'),
            hops_from_seed=response.meta.get('hops_from_seed'),
            file_urls=file_urls,
        )
