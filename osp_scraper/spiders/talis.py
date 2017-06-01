# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import scrapy

from ..spiders.CustomSpider import CustomSpider

class TalisSpider(CustomSpider):
    name = "talis"

    # TEST CODE - TO BE REMOVED BEFORE MERGE:
    database_urls = [
        "https://uq.rl.talis.com/index.html",
        "https://scu.rl.talis.com/index.html",
        "https://latrobe.rl.talis.com/index.html",
        "https://murdoch.rl.talis.com/index.html",
        "https://griffith.rl.talis.com/index.html",
        "https://deakin.rl.talis.com/index.html",
        "http://resourcelists.ntu.ac.uk/index.html",
        "https://mmu.rl.talis.com/index.html",
        "https://brunel.rl.talis.com/index.html",
        "http://readinglists.nottingham.ac.uk/index.html",
        "http://readinglists.city.ac.uk/index.html",
        "http://resourcelists.coventry.ac.uk/index.html",
        "https://derby.rl.talis.com/index.html",
        "http://aspire.surrey.ac.uk/index.html",
        "http://readinglists.ucl.ac.uk/index.html",
        "http://liblists.sussex.ac.uk/index.html",
        "https://hull.rl.talis.com/index.html",
        "http://lists.exeter.ac.uk/index.html",
        "http://readinglists.bournemouth.ac.uk/index.html",
        "https://brookes.rl.talis.com/index.html",
        "https://kcl.rl.talis.com/index.html",
        "https://port.rl.talis.com/index.html",
        "http://lists.library.lincoln.ac.uk/index.html",
        "http://resourcelists.roehampton.ac.uk/index.html",
        "https://plymouth.rl.talis.com/index.html",
        "http://lists.lib.keele.ac.uk/index.html",
        "http://resourcelists.falmouth.ac.uk/index.html",
        "http://resourcelists.rgu.ac.uk/index.html",
        "http://resourcelists.ed.ac.uk/index.html",
        "http://readinglists.warwick.ac.uk/index.html",
        "http://lists.bolton.ac.uk/index.html",
        "https://manchester.rl.talis.com/index.html",
        "http://cypruslists.central-lancashire.ac.uk/index.html",
        "http://readinglists.central-lancashire.ac.uk/index.html",
        "https://mdx.rl.talis.com/index.html",
        "https://essex.rl.talis.com/index.html",
        "https://hope.rl.talis.com/index.html",
        "https://lancaster.rl.talis.com/index.html",
        "http://readinglists.glasgow.ac.uk/index.html",
        "http://aspire.aber.ac.uk/index.html",
        "http://readinglists.le.ac.uk/index.html",
        "https://stirling.rl.talis.com/index.html",
        "https://dundee.rl.talis.com/index.html",
        "https://uea.rl.talis.com/index.html",
        "http://resourcelists.st-andrews.ac.uk/index.html",
        "https://bangor.rl.talis.com/index.html",
        "https://dmu.rl.talis.com/index.html",
        "https://rhul.rl.talis.com/index.html",
        "https://shu.rl.talis.com/index.html",
        "http://readinglists.northampton.ac.uk/index.html",
        "https://gold.rl.talis.com/index.html",
        "https://qmul.rl.talis.com/index.html",
        "https://brighton.rl.talis.com/index.html",
        "https://glam.rl.talis.com/index.html",
        "https://winchester.rl.talis.com/index.html",
        "http://readinglists.harper-adams.ac.uk/index.html",
        "http://readinglist.bi.edu/index.html",
        "https://auckland.rl.talis.com/index.html",
        "https://victoria.rl.talis.com/index.html",
        "https://waikato.rl.talis.com/index.html"
    ]

    def start_requests(self):
        for url in self.database_urls:
            # Search for anything with a space in it
            yield scrapy.Request(
                urljoin(url, "/search.html?q=+"),
                meta={
                    'depth': 0,
                    'hops_from_seed': 0
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        for a_tag in response.css("#search_results_lists ol a"):
            anchor = a_tag.css("::text").get()
            yield response.follow(
                a_tag,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )

        next_url = response.css("#search_results_lists .pagination")\
            .css("li:nth-child(3) a::attr(href)")\
            .get()
        if next_url:
            yield response.follow(
                next_url,
                meta={
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_courses
            )

    def extract_links(self, response):
        title = response.css("#pageTitle::text").get()
        url = response.css("#exportsToRIS::attr(href)").get()
        yield (url, title)
