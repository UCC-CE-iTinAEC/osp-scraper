# -*- coding: utf-8 -*-

import itertools
import scrapy

from ..spiders.CustomSpider import CustomSpider

class SHSUSpider(CustomSpider):
    name = "shsu"
    allowed_domains = ["shsu.edu"]

    def start_requests(self):
        start_url = "https://ww2.shsu.edu/faci10wp/"

        def get_terms(response):
            years = response.css("select[name='year'] option::attr(value)")
            semesters = response.css("select[name='semester'] option::attr(value)")
            searches = itertools.product(years.extract(), semesters.extract())
            for year, semester in searches:
                yield scrapy.FormRequest(
                    response.urljoin('display.php'),
                    method="POST",
                    formdata={
                        'semester': semester,
                        'year': year,
                        # '-' means search all departments.
                        'dept': "-",
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': year + " " + semester,
                    },
                    callback=self.parse_for_files
                )

        yield scrapy.Request(start_url, callback=get_terms)

    def extract_links(self, response):
        tags_root = response.css("tr.noshade td:nth-child(2)")
        # Each cell contains multiple course sections that need to be selected.
        syllabus_links = tags_root.css("font ~ span")
        class_numbers = tags_root.css("font")
        for syllabus, number in zip(syllabus_links, class_numbers):
            link = syllabus.css("a::attr(href)").extract_first()
            # Skip iteration if the course doesn't have a syllabus link.
            if not link:
                continue
            url = response.urljoin(link)
            number_text = number.css("font::text").extract_first()
            # The anchor contains lots of CRLF line endings, so clean it up.
            anchor = " ".join(number_text.split())
            yield (url, anchor)
