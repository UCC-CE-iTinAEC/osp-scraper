# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ReedleySpider(CustomSpider):
    name = "reedley"
    allowed_domains = ["reedleycollege.edu"]

    def start_requests(self):
        start_url = "http://reedleycollege.edu/index.aspx?page=903"

        def open_folders(response):
            tags = response.css('#_ctl0_listDataGrid tr td:nth-child(2) a')
            # The hrefs for links that are not folders are documents that
            # need to be sent through the pipeline.
            if response.meta['hops_from_seed'] != 0:
                for item in self.parse_for_files(response):
                    print('inside', response.meta['source_anchor'], response.meta['depth'])
                    yield item

            for tag in tags:
                # The hrefs for links that are folders are javascript commands,
                # so extract the useful bits to be used in recursive POST
                # requests that open those folders.
                link = tag.css('::attr(href)').re_first(r'_ctl0.*?_ctl0')
                if link:
                    event_target = link.replace('$', ':')
                    anchor = tag.css('a::text').extract_first()
                    print(event_target, anchor)

                    yield scrapy.FormRequest.from_response(
                        response,
                        formdata={
                            '__EVENTTARGET': event_target,
                        },
                        meta={
                            'depth': 1,
                            'hops_from_seed': 1,
                            'source_url': response.url,
                            'source_anchor': anchor,
                            'require_files': True
                        },
                        method='POST',
                        callback=open_folders
                    )

        yield scrapy.Request(start_url, meta={'hops_from_seed': 0}, callback=open_folders)

    def extract_links(self, response):
        for tag in response.css('#_ctl0_listDataGrid tr td:nth-child(2)'):
            link = tag.css('a::attr(href)').extract_first()
            if not 'javascript' in link:
                anchor = tag.css('a::text').extract_first()
                url = response.urljoin(link)
                yield (url, anchor)
