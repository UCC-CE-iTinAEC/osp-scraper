# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class NiagaraCollegeSpider(CustomSpider):
    """
    This site is a multi-part form (Subject, Catalogue Number, Term) where the
    list of options for each field is loaded in by a POST request after
    selecting an option for the previous field.  To simulate this,
    `dont_click=True` is used.
    """

    name = "niagaracollege"

    start_urls = ["https://ess.niagaracollege.ca/CourseOutline/Default.aspx"]

    def parse(self, response):
        subjects = response.css("#ctl00_ContentPlaceholderMain_ListBoxLookupSubject")\
                           .css("option::attr(value)")[1:].extract()
        for subject in subjects:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    '__EVENTTARGET':
                        "ctl00$ContentPlaceholderMain$ListBoxLookupSubject",
                    'ctl00$ContentPlaceholderMain$ListBoxLookupSubject':
                        subject
                },
                meta={
                    'subject': subject
                },
                dont_click=True,
                callback=self.parse_for_catalogue_numbers
            )

    def parse_for_catalogue_numbers(self, response):
        numbers = response.css("#ctl00_ContentPlaceholderMain_ListBoxLookupCatalogueNumber")\
                          .css("option::attr(value)")[1:].extract()
        for number in numbers:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    '__EVENTTARGET':
                        'ctl00$ContentPlaceholderMain$ListBoxLookupCatalogueNumber',
                    'ctl00$ContentPlaceholderMain$ListBoxLookupCatalogueNumber':
                        number
                },
                meta={
                    'subject': response.meta['subject'],
                    'number': number
                },
                dont_click=True,
                callback=self.parse_for_terms
            )

    def parse_for_terms(self, response):
        terms = response.css("#ctl00_ContentPlaceholderMain_ListBoxLookupAcademicTerm")\
                        .css("option")
        for term in terms:
            term_code = term.css('::attr(value)').extract_first()
            term_text = term.css('::text').extract_first()
            anchor = " ".join([
                response.meta['subject'],
                response.meta['number'],
                term_text
            ])
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'ctl00$ContentPlaceholderMain$ListBoxLookupAcademicTerm':
                        term_code,
                    'ctl00$ContentPlaceholderMain$ButtonLookupCourseOutline':
                        'Lookup Outline'
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        # Either we've landed on an HTML course outline or there will be a
        # download link.  The href is javascript, so extract the relevant
        # relative url.
        rel_url = response.css("#ctl00_ContentPlaceholderMain_LinkButtonDownloadOutline::attr(href)")\
                          .re_first('.*"(external.aspx.*)"')
        if rel_url:
            url = response.urljoin(rel_url)
            anchor = response.css("#code-bar h4::text").extract()[-1]
            yield(url, anchor)
