# -*- coding: utf-8 -*-

import itertools

import scrapy

from ..spiders.CustomSpider import CustomSpider

class KAISTSpider(CustomSpider):
    """
    There is some sort of "session timeout" feature on the search entry page of
    this site, as well as some sort of queuing feature for when multiple people
    are accessing the site, both of which could potentially affect the operation
    of the scraper if run over long periods.

    If a syllabus link is available on a course page, it is scraped; if a
    syllabus link is not available, the course page itself is scraped.  It seems
    like most syllabus links contain all the information available on the course
    pages.
    """
    name = "kaist"

    start_urls = ["https://cais.kaist.ac.kr/totalOpeningCourse"]

    def parse(self, response):
        years = response.css("#sel_year option::attr(value)").getall()
        terms = response.css("#sel_term option")
        for year, term in itertools.product(years, terms):
            term_value = term.css("::attr(value)").get()
            term_text = term.css("::text").get()

            anchor = " ".join([year, term_text])

            # The department field is populated by a "refresh" action based on
            # what year and term are selected.
            yield scrapy.FormRequest(
                "https://cais.kaist.ac.kr/refreshComboBox",
                method="POST",
                formdata={
                    'year': year,
                    'term': term_value,
                    # 'idname' can be other form entry fields, but the one for
                    # department seems the most useful.
                    'idname': 'sel_dept',
                    'lang': 'ENG'
                },
                meta={
                    'year': year,
                    'term': term_value,
                    'anchor': anchor
                },
                callback=self.parse_for_departments
            )

    def parse_for_departments(self, response):
        # We could just search 'ALL' departments, but if there are too many
        # results, the site will ask to download an spreadsheet instead, which
        # we don't want.
        depts = response.css("#sel_dept option")
        for dept in depts[1:]:
            dept_value = dept.css("::attr(value)").get()
            dept_text = dept.css("::text").get()

            anchor = response.meta["anchor"] + " " + dept_text

            yield scrapy.FormRequest(
                "https://cais.kaist.ac.kr/totalOpeningCourse",
                method="POST",
                formdata={
                    'processType': "content",
                    'sel_year': response.meta['year'],
                    'sel_term': response.meta['term'],
                    'sel_dept': dept_value,
                    'sel_course': '%',
                    'sel_subject': '%',
                    'sel_lang': 'A'
                },
                meta={
                    'year': response.meta['year'],
                    'term': response.meta['term'],
                    'dept': dept_value,
                    'anchor': anchor
                },
                callback=self.parse_for_coursepages
            )

    def parse_for_coursepages(self, response):
        coursepage_url = "https://cais.kaist.ac.kr/syllabusInfo"
        rows = response.css("#contentTable tbody tr")

        for row in rows:
            a_tag = row.css("a[name='syllabusView']")
            if a_tag:
                course_title = a_tag.css("::text").get()
                subject_no = row.css("td:nth-child(6)::text").get()
                lecture_class = row.css("td:nth-child(7)::text").get()

                anchor = " ".join([
                    response.meta['anchor'],
                    course_title,
                    subject_no,
                    lecture_class
                ])

                # NOTE: Need to be careful with the FormRequest below: as long
                # as all the formdata fields are populated with something, a 200
                # response is returned, even if it's junk that leads to an empty
                # HTML page.
                yield scrapy.FormRequest(
                    coursepage_url,
                    method="GET",
                    formdata={
                        'year': response.meta['year'],
                        'term': response.meta['term'],
                        'subject_no': subject_no,
                        'lecture_class': lecture_class,
                        'dept_id': response.meta['dept']
                    },
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': anchor,
                        'year': response.meta['year'],
                        'term': response.meta['term'],
                        'subject_no': subject_no,
                        'lecture_class': lecture_class,
                        'dept_id': response.meta['dept']
                    },
                    callback=self.parse_for_syllabi
                )

    def parse_for_syllabi(self, response):
        # The syllabus link is hidden behind a POST request, so we can't just
        # use `extract_links`.
        a_value = response.css("#fileDownLink::attr(value)").get()
        # Some `a_value`s are the string "None", so check a_text as well.
        a_text = response.css("#fileDownLink::text").get()
        if a_value and a_text:
            anchor = response.meta['source_anchor'] + " " + a_text

            yield scrapy.FormRequest(
                "https://cais.kaist.ac.kr/fileDown",
                method="POST",
                formdata={
                    'serverFileName': a_value,
                    'realFileName': a_text,
                    'fileDownGubun': 'syllabus',
                    'year': response.meta['year'],
                    'term': response.meta['term'],
                    'subject_no': response.meta['subject_no'],
                    'lecture_class': response.meta['lecture_class'],
                    'dept_id': response.meta['dept_id']
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
        else:
            # When a syllabus link isn't available, pull the course page itself.
            for item in self.parse_for_files(response):
                yield item
