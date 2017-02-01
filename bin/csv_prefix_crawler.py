#!/usr/bin/env python3

import sys
import os.path
import csv

import osp_scraper.tasks
from osp_scraper.spiders import url_to_prefix_params

def main(csv_file):
    with open(csv_file) as f:
        for row in csv.reader(f):
            osp_scraper.tasks.crawl.delay(**url_to_prefix_params(row[0]))

def usage():
    print("%s <csv_file>" % os.path.basename(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    else:
        main(sys.argv[1])
