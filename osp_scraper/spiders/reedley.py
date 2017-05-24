# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class ReedleySpider(CustomSpider):
    name = "reedley"

    start_urls = ["http://reedleycollege.edu/index.aspx?page=903"]

    def parse(self, response):
        tags = response.css('#_ctl0_listDataGrid tr td:nth-child(2) a')
        for tag in tags:
            href = tag.css('::attr(href)')
            anchor = tag.css('a::text').get()
            path = response.meta.get("source_anchor", "") + "/" + anchor

            if href.get().startswith("javascript"):
                # The hrefs for links that are folders are javascript commands,
                # so extract the useful bits to be used in recursive POST
                # requests that open those folders.
                folder_link = href.re_first(r'_ctl0.*?_ctl0')
                event_target = folder_link.replace('$', ':')

                yield scrapy.FormRequest.from_response(
                    response,
                    method='POST',
                    formdata={
                        '__EVENTTARGET': event_target,
                    },
                    meta={
                        'depth': response.meta["depth"] + 1,
                        'hops_from_seed': response.meta["hops_from_seed"] + 1,
                        'source_anchor': path
                    },
                    callback=self.parse
                )
            else:
                yield response.follow(
                    href.get(),
                    meta={
                        'depth': response.meta["depth"] + 1,
                        'hops_from_seed': response.meta["hops_from_seed"] + 1,
                        'source_url': response.url,
                        'source_anchor': path
                    },
                    callback=self.parse_for_files
                )
