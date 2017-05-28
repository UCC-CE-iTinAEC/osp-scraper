# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TTUSpider(CustomSpider):
    name = "ttu"

    start_urls = ["http://catalog.ttu.edu/content.php?catoid=2&navoid=163"]

    custom_settings = {
        **CustomSpider.custom_settings,
        'USER_AGENT': "Mozilla/5.0"
    }

    def parse(self, response):
        prefixes = response\
            .css("select[name='filter[27]'] option::attr(value)")\
            .getall()[1:]
        for prefix in prefixes:
            # convert prefix to hexadecimal ASCII representation
            hex_prefix = "".join(format(ord(c), "X") for c in prefix)
            yield scrapy.FormRequest(
                "http://appserv.itts.ttu.edu/PACI/Pages/Search/SearchResults.aspx",
                method="GET",
                formdata={
                    '7374797065': "434F55525345",
                    '63707265666978': hex_prefix,
                    '636E756D': "",
                    '637469746C65': ""
                },
                meta={
                    'depth': 1,
                    'hops_from_seed': 1,
                    'source_url': response.url,
                    'source_anchor': prefix + " Page 1",
                    'page': 1,
                    'prefix': prefix
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for item in self.parse_for_files(response):
            yield item

        page = response.meta["page"] + 1
        prefix = response.meta["prefix"]

        # __EVENTVALIDATION and __VIEWSTATE are included in a form in the first
        # page response, but they sometimes change when the page changes, and
        # the new values are included in a strange format in the HTML partials.
        first_response = response.meta.get('first_response', response)
        extra_form_data = {
            '__EVENTVALIDATION':
                response.selector.re_first(r"\|__EVENTVALIDATION\|(.*?)\|"),
            '__VIEWSTATE':
                response.selector.re_first(r"\|__VIEWSTATE\|(.*?)\|")
        } if page > 2 else {}

        yield scrapy.FormRequest.from_response(
            first_response,
            headers={
                'Accept': "*/*",
                'X-MicrosoftAjax': 'Delta=true'
            },
            formdata={
                '__ASYNCPOST': "true",
                '__LASTFOCUS': "",
                'ctl00$ContentPlaceHolder1$ddl_CoursePageSize': "10",
                'ctl00$ScriptManger1': "ctl00$ContentPlaceHolder1$SearchResultsUpdatePanel|ctl00$ContentPlaceHolder1$CourseResultsGridView",
                '__EVENTTARGET': "ctl00$ContentPlaceHolder1$CourseResultsGridView",
                'ctl00$SideMenu1$searchControl$searchBtn': None,
                '__EVENTARGUMENT': "Page$" + str(page),
                **extra_form_data
            },
            meta={
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
                'source_url': response.url,
                'source_anchor': " ".join([prefix, "Page", str(page)]),
                'page': page,
                'prefix': prefix,
                'first_response': first_response
            },
            callback=self.parse_for_courses
        )

    def extract_links(self, response):
        rows = response.css("#ctl00_ContentPlaceHolder1_CourseResultsGridView tr")
        for row in rows:
            url = row.css("td:nth-child(8) .ResultLinkButton::attr(href)").get()
            if url:
                anchor = " ".join(row.css("td")[:6].css("::text").getall())
                yield (url, anchor)
