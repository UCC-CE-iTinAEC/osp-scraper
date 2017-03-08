# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class BrevardSpider(CustomSpider):
    name = "brevard"
    allowed_domains = ["easternflorida.edu"]

    def start_requests(self):
        start_url = 'http://web12.easternflorida.edu/ecpr/choice.cfm'

        def select_search(response):
            # for repository in response.css('a.copyBold15::attr(href)'):
            # repository_link = response.css('a.copyBold15::attr(href)').extract()
            # repository_anchor = response.css('a.copyBold15::text').extract()
            # for link, anchor in zip(repository_link, repository_anchor):
                # print('Running {0},{1}'.format(anchor, link))
                # yield scrapy.Request(
                        # response.urljoin(link),
                        # method="GET",
                        # meta={
                            # "depth": 1,
                            # "hops_from_seed": 1,
                            # "source_url": response.url,
                            # "source_anchor": anchor,
                        # },
                        # callback=enter_search
                # )
            yield scrapy.Request(
                'http://web12.easternflorida.edu/ecpr/choice.cfm?CC=1',
                meta={
                    "depth": 1,
                    "hops_from_seed": 1,
                    "source_url": response.url,
                    "source_anchor": "",
                },
                callback=enter_search
            )

        def enter_search(response):
            # Scrape all subsequent pages
            print('Entering search')
            yield scrapy.FormRequest.from_response(
                    response,
                    formdata={
                        'Search': 'Search',
                    },
                    meta={
                        "depth": response.meta['depth'] + 1,
                        "hops_from_seed": response.meta["hops_from_seed"] + 1,
                        "source_url": response.url,
                        "source_anchor": "",
                    },
                    method='POST',
                    callback=select_page
            )

        def select_page(response):
            if response.css('table tr td table a::attr(href)'):
                self.parse_for_files(response)
                print('Ran parse_for_files on ' + response.url)
            else:
                return

            print(response.css('table tr td[align="left"] a::attr(href)').extract())
            next_btn = response.css('table tr td[align="left"] a::attr(href)').extract()[-1]
            yield scrapy.Request(
                    response.urljoin(next_btn),
                    method='GET',
                    meta={
                        "depth": response.meta['depth'],
                        "hops_from_seed": response.meta["hops_from_seed"] + 1,
                        "source_url": response.url,
                        "source_anchor": "",
                    },
                    callback=select_page
            )

        yield scrapy.Request(start_url, callback=select_search, dont_filter=True)

    def extract_links(self, response):
        print("Running extract links on " + response.url)
        for tag in response.css('a.text10'):
            url = response.urljoin(tag.css('a::attr(href)').extract_first())
            anchor = tag.css('a::text')
            print("Downloading {0},{1}".format(anchor, url))
            yield (url, anchor)
