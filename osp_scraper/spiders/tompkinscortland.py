# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TompkinsCortlandSpider(CustomSpider):
    name = "tompkinscortland"

    start_urls = ["http://www.tompkinscortland.edu/catalog/cs_disciplines.asp"]

    def parse(self, response):
        disciplines = response.css("#content_area a::attr(href)").getall()
        for discipline in disciplines:
            yield response.follow(discipline, callback=self.parse_for_pages)

    def parse_for_pages(self, response):
        pages = response.css(".trTableFooterPager a::text").getall()
        for page in pages:
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    '__EVENTTARGET': "ctl00$mainContent$gvCourses",
                    '__EVENTARGUMENT': "Page$" + page
                },
                callback=self.parse_for_courses
            )

        for request in self.parse_for_courses(response):
            yield request

    def parse_for_courses(self, response):
        courses = response.css("tr td:first-child")
        for course in courses:
            course_url = course.css("br+a::attr(href)").get()
            if course_url:
                course_name = " ".join(course.css("::text").getall())
                yield response.follow(
                    course_url,
                    meta={
                        'depth': 1,
                        'hops_from_seed': 1,
                        'source_url': response.url,
                        'source_anchor': course_name,
                    },
                    callback=self.parse_for_files
                )

    def extract_links(self, response):
        course_name = response.css(".catCourseName::text").get()
        for a_tag in response.css("a"):
            url = a_tag.css("::attr(href)").get()
            anchor = " ".join(a_tag.css("::text").getall())
            if url and "syllabus" in anchor.lower():
                yield (url, course_name + " " + anchor)
