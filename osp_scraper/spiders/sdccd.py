# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SDCCDSpider(CustomSpider):
    name = "sdccd"

    start_urls = ["http://schedule.sdccd.edu/index.cfm"]


    def parse(self, response):
        terms = response.css("select[name='trm'] option")[1:]
        for term in terms:
            value = term.css("::attr(value)").extract_first()
            anchor = term.css("::text").extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    # 'resetfilters' seems to populate the different form fields
                    # based on the value of 'trm'.
                    'selectaction': "resetfilters",
                    'trm': value
                },
                meta={
                    'source_anchor': anchor,
                    'trm': value
                },
                callback=self.parse_for_campus_and_subject
            )

    def parse_for_campus_and_subject(self, response):
        campuses = response.css("select[name='campus'] option")[1:]
        campus_values = campuses.css("::attr(value)").extract()
        campus_anchors = campuses.css("::text").extract()
        subjs = response.css("select[name='subj'] option")[1:]
        subj_values = subjs.css("::attr(value)").extract()
        subj_anchors = subjs.css("::text").extract()

        for campus_value, campus_anchor in zip(campus_values, campus_anchors):
            for subj_value, subj_anchor in zip(subj_values, subj_anchors):
                anchor = ' '.join([response.meta['source_anchor'],
                                   campus_anchor,
                                   subj_anchor])
                yield scrapy.FormRequest.from_response(
                    response,
                    method="POST",
                    formname="ClassSelectForm",
                    formdata={
                        'selectaction': "listschedule",
                        'trm': response.meta['trm'],
                        'campus': campus_value,
                        'subj': subj_value
                    },
                    meta={
                        'source_anchor': anchor,
                        'trm': response.meta['trm'],
                        'campus': campus_value,
                        'subj': subj_value
                    },
                    callback=self.parse_for_courses
                )

    def parse_for_courses(self, response):
        # The courses options are populated based on the chosen subject, and so
        # need to be selected in separate requests.
        courses = response.css("select[name='crse'] option")[1:]
        for course in courses:
            value = course.css("::attr(value)").extract_first()
            course_name = course.css("::text").extract_first()
            anchor = response.meta['source_anchor'] + " " + course_name
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formname="ClassSelectForm",
                formdata={
                    'selectaction': 'listschedule',
                    'trm': response.meta['trm'],
                    'campus': response.meta['campus'],
                    'subj': response.meta['subj'],
                    'crse': value
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'require_files': True
                },
                callback=self.parse_for_pages
            )

    def parse_for_pages(self, response):
        # NOTE: I'm not actually sure if there are any cases of multi-page
        # results for a search with term, campus, subject and course specified,
        # but the below should work in case there are any.
        for item in self.parse_for_files(response):
            yield item

        # For multi-page search results, there is a row of pages on the top and the
        # bottom.  Each row looks like this:
        #           | 1 | 2 | ... | N |
        # Where the current page is given the 'redbold' class and each '|' is
        # inside a <strong>.
        next_page = response.css("td.worksheet_msg_text")\
                            .css("span.redbold + strong + a::text")
        if next_page:
            number = self.clean_whitespace(next_page[0].extract())
            anchor = response.meta['source_anchor'] + " Page " + number
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formname="pagination",
                formdata={
                    'selectaction': 'listschedule',
                    'page': number
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'require_files': True
                },
                callback=self.parse_for_pages
            )

    def extract_links(self, response):
        # NOTE: 'details' and 'books' are both always html, but I found this to
        # be a nice case for `extract_links` anyway.
        details = response.css("a[title~='Class']")
        for detail in details:
            # The details link 'onclick' element looks like this:
            # Open_the_Window('<rel_url>', ...[other parameters]...)
            rel_url = detail.css("::attr(onclick)").extract_first().split("'")[1]
            url = response.urljoin(rel_url)
            anchor = response.meta['source_anchor'] + " " + detail.css("::text")\
                                                                  .extract_first()
            yield (url, anchor)

        books_url = (
            "http://schedule.sdccd.edu/book/book.cfm"
            "?crn={0}"
            "&term={1}"
            "&campus={2}"
            "&instructor={3}"
            "&dept={4}"
            "&course={5}"
            "&coursedescription={6}"
        )

        books = response.css("span[title='Textbook']")
        for book in books:
            # The book link 'onclick' element looks like this:
            # openbook('<crn>','<term code>', '<college code> ','<instructor>','<course initials>','<course number>','<course title>')
            book_codes = book.css("::attr(onclick)").re(r"'(.*?)'")
            url = books_url.format(*book_codes)
            anchor = response.meta['source_anchor'] + " " + book_codes[0] + " Book"

            yield (url, anchor)
