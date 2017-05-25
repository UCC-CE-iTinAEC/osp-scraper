# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class FHSUSpider(CustomSpider):
    """
    The form on page http://webapps.fhsu.edu/OnlineSyllabus/ leads to URLs that
    are of the form seen below.  It was non-trivial to implement searches
    through the form itself, so instead, this scraper grabs the files at all
    urls of this form.  Currently, the URLs lead to files up to id=593.  The
    scraper looks for files up to id=1000 for some amount of future proofing.
    """

    name = "fhsu"

    custom_settings = {
        'RETRY_ENABLED': False
    }

    def start_requests(self):
        url_format = "https://webapps.fhsu.edu/portal/WebParts/wpSyllabus/ViewSyllabus.aspx?id={}&cp=0"
        for i in range(0, 1000):
            yield scrapy.Request(
                url_format.format(i),
                meta={
                    'depth': 0,
                    'hops_from_seed': 0,
                    'source_url': "http://webapps.fhsu.edu/OnlineSyllabus/",
                    'source_anchor': "ID: " + str(i)
                },
                callback=self.parse_for_files
            )
