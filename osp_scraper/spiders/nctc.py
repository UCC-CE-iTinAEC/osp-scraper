# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class NCTCSpider(CustomSpider):
    """
    Every course page exposed in the search of this site contains one of the
    following:
    1) No syllabi.
    2) An HTML syllabus on the same page.
    3) A link to a syllabus (doc, docx, pdf).
    4) Both 2) and 3).
    There unfortunately seems to be no easy way to prune out instances of 1)
    without increasing the number of requests, and there also seems to be no
    particularly clean way to avoid duplicate collection during instances of 4).
    """
    name = "nctc"

    start_urls = ["https://my.nctc.edu/ICS/Academics"]

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            method="POST",
            formdata={
                'ctl05$tbSearch': 'Search...',
                'pg2$V$ddlTerm': 'All',
                'pg2$V$btnSubmit': 'Search'
            },
            meta={
                'depth': 1,
                'hops_from_seed': 1,
                'page': '1'
            },
            callback=self.parse_for_pages
        )

    def parse_for_pages(self, response):
        for request in self.parse_for_courses(response):
            yield request

        # NOTE: This site is extremely "sensitive": if requests aren't done in
        # the "right" order, it will often redirect to page complaining about
        # the user having used the Back or Refresh button
        # (https://my.nctc.edu/ICS/default.aspx).  The best way to manage this
        # seems to be to simulate next page button presses only, and to not use
        # from_response.
        next_page = response.css("a.nextPage::attr(href)")\
                            .re_first(r".*\('pg2\$V\$pNav','([0-9]+)'\)")
        if next_page:
            viewstate = response.css("#__VIEWSTATE::attr(value)").extract_first()
            viewstategenerator = response.css("#__VIEWSTATEGENERATOR::attr(value)")\
                                         .extract_first()
            browserrefresh = response.css("#___BrowserRefresh::attr(value)")\
                                     .extract_first()
            yield scrapy.FormRequest(
                response.url,
                method="POST",
                formdata={
                    '__EVENTTARGET': "pg2$V$pNav",
                    '__EVENTARGUMENT': next_page,
                    '__VIEWSTATE': viewstate,
                    '__VIEWSTATEGENERATOR': viewstategenerator,
                    '___BrowserRefresh': browserrefresh,
                    'ctl05$tbSearch': "Search...",
                    'pg2$V$ddlTerm': "All"
                },
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'page': str(int(next_page) + 1)
                },
                callback=self.parse_for_pages
            )

    def parse_for_courses(self, response):
        rows = response.css("tbody.gbody tr:nth-child(odd)")
        for row in rows:
            course_code = row.css("td:first-child::text").extract_first()
            faculty = row.css("td:nth-child(3) div.nobr::text").extract_first()
            course = row.css("td:nth-child(2) a::text").extract_first()
            rel_url = row.css("td:nth-child(2) a::attr(href)").extract_first()
            url = response.urljoin(rel_url)
            anchor = course_code + course + faculty
            yield scrapy.Request(
                url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor + " Page " + response.meta['page']
                },
                callback=self.parse_for_files
            )

    def extract_links(self, response):
        tag = response.css("span[id$='spanProtectedItemLink'] a")
        if tag:
            rel_url = tag.css("::attr(href)").extract_first()
            url = response.urljoin(rel_url)
            tag_text = tag.css("::text").extract_first()
            title_bar = response.css("#contextName::text").extract_first()
            anchor = title_bar + " " + tag_text
            yield (url, anchor)
