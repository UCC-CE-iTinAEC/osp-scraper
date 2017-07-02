# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class KDGSpider(CustomSpider):
    """
    This site responds with multiple redirects for several of the requests, but
    unfortunately, there doesn't seem to be an easy way to avoid that behavior.
    """
    name = "kdg"

    start_urls = ["https://ects.kdg.be/"]

    def parse(self, response):
        # We could search here by year and department, but the year selection
        # can be used to refresh the department list, so we do that first.
        years = response.css("#MainContent_ddlAcaj option::attr(value)").getall()
        for year in years:
            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    '__EVENTTARGET': "ctl00$MainContent$ddlAcaj",
                    'ctl00$MainContent$ddlAcaj': year,
                    'ctl00$btnHome': None
                },
                meta={
                    'year': year
                },
                callback=self.parse_for_departments
            )

    def parse_for_departments(self, response):
        depts = response.css("#MainContent_ddlOpld option")
        for dept in depts:
            dept_value = dept.css("::attr(value)").get()
            dept_text = dept.css("::text").get()
            anchor = response.meta['year'] + " " + dept_text

            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    'ctl00$MainContent$ddlAcaj': response.meta['year'],
                    'ctl00$MainContent$ddlOpld': dept_value,
                    'ctl00$MainContent$btnTraj': 'Naar Studiegids'
                },
                meta={
                    'anchor': anchor
                },
                callback=self.parse_for_modules
            )

    def parse_for_modules(self, response):
        base_url = "https://ects.kdg.be/frmProgram?odtj={0}"

        a_tags = response.css("a[id^='MainContent_tvwTrajectt']")[1:]
        for a_tag in a_tags:
            # hrefs look like this:
            #   javascript:__doPostBack('<eventtarget>','s\\<module_num>')"
            num = a_tag.css("::attr(href)").re_first(r"'s\\\\(.*)'\)")
            a_text = a_tag.css("::text").get()
            anchor = response.meta['anchor'] + " " + a_text

            yield scrapy.Request(
                base_url.format(num),
                meta={
                    'anchor': anchor
                },
                callback=self.parse_for_programs
            )

    def parse_for_programs(self, response):
        a_tags = response.css("a[id^='MainContent_lvwProgram_OlodSelect_']")
        for a_tag in a_tags:
            # hrefs look like this:
            #   javascript:__doPostBack('<eventtarget>','')
            eventtarget = a_tag.css("::attr(href)").re_first("'(.*?)'")
            a_text = a_tag.css("::text").get()
            anchor = response.meta['anchor'] + " " + a_text

            yield scrapy.FormRequest.from_response(
                response,
                method="POST",
                formdata={
                    '__EVENTTARGET': eventtarget,
                    'ctl00$btnHome': None
                },
                meta={
                    'depth': 3,
                    'hops_from_seed': 3,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
