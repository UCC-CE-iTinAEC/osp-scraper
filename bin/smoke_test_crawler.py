#!/usr/bin/env python3

import sys
import os.path
import csv
import logging

from syllascrape.spiders import Spider
from syllascrape.spiders import url_to_prefix_params

from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor


def main(csv_file):
    with open(csv_file) as f:
        row = next(csv.reader(f))

    kwargs = url_to_prefix_params(row[0])
    print(kwargs)

    process = CrawlerProcess(get_project_settings())
    process.crawl(Spider, **kwargs)
    process.start()


    #runner = CrawlerRunner(get_project_settings())
    #d = runner.crawl(Spider, )
    #d.addBoth(lambda _: reactor.stop())
    #print("STARTING REACTOR")
    #reactor.run()


def usage():
    print("%s <csv_file>" % os.path.basename(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    else:
        main(sys.argv[1])