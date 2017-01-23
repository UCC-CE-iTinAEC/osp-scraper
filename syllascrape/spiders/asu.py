# -*- coding: utf-8 -*-

import scrapy
from ..items import PageItem 
from ..spiders.CustomSpider import CustomSpider

class ASUSpider(CustomSpider):
    name = "asu"
    allowed_domains = ["asu.edu"]

    def start_requests(self):
        terms = []
        subjects = []

        start_url = "https://webapp4.asu.edu/catalog/"

        def get_terms_codes(response):
            for option in response.css("#term option"):
                code = option.css("option::attr(value)").extract_first()
                name = option.css("option::text").extract_first()
                terms.append((code, name))

            yield scrapy.Request("https://webapp4.asu.edu/catalog/Subjects.html", callback=get_subject_codes)

        def get_subject_codes(response):
            for subject in response.css("#subjectDivs .row"):
                code = subject.css(".subject::text").extract_first()
                name = subject.css(".subjectTitle::text").extract_first()
                subjects.append((code, name))

            for term_code, term_name in terms[:3]:
                for subject_code, subject_name in subjects[:3]:
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
                            "source_anchor": subject_name + " " + term_name,
                        },
                        callback=self.parse_for_files
                    )

        yield scrapy.Request(start_url, callback=get_terms_codes, dont_filter=True)

    def get_file_links(self, response):
        for tag in response.css('a[title="Syllabus"]'):
            url = tag.css('a::attr(href)').extract_first()
            if url:
                anchor = tag.css('a::text').extract_first()
                yield (url, anchor)
