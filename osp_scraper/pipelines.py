# -*- coding: utf-8 -*-

import scrapy
from scrapy.pipelines.files import FilesPipeline

import warc
import httpstatus

import socket
import uuid
import logging
import os.path
import time
import json
import itertools
from io import BytesIO
from urllib.parse import urlparse

from . import items
from .version import git_revision

def path_from_warc(record, prefix=""):
    """return a path from the Record ID of a WARC"""
    path = "%s.warc" % record.header.record_id[10:-1]
    return os.path.join(prefix, path)

def new_warc(kind):
    """return a new WARCRecord

    @arg kind: what flavor of WARC to create; see `warc.WarcHeader.CONTENT_TYPES` for flavors
    """

    # ripped from WARCHeader.init_defaults()
    headers = {

        'WARC-Type': kind,
        'WARC-Record-ID': "<urn:uuid:%s>" % uuid.uuid1(),
        'Content-Type': warc.WARCHeader.CONTENT_TYPES[kind],
        'WARC-Date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

    return warc.WARCRecord(header=warc.WARCHeader(headers, defaults=False),
                           defaults=False)

def update_warc_info_from_spider(record, spider):
    """update a WARC warcinfo record from a scrapy Spider"""

    # make empty header object to use for fields
    # XXX WARCHeader messes up capitalization here
    fields = warc.WARCHeader({}, defaults=False)
    fields['software'] = 'osp_scraper'
    fields['hostname'] = socket.getfqdn()
    fields['x-spider-name'] = spider.name
    fields['x-spider-run-id'] = spider.run_id
    fields['x-spider-revision'] = git_revision
    fields['x-spider-parameters'] = json.dumps(spider.get_parameters())

    buf = BytesIO()
    fields.write_to(buf, version_line=False, extra_crlf=False)
    record.update_payload(buf.getvalue())


def update_warc_response_from_item(record, item):
    """update a WARC response record from a scrapy Item"""
    h = record.header
    h['WARC-Target-URI'] = item['url']
    h['WARC-Date'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(item['retrieved']))
    h['X-Spider-Name'] = item['spider_name']
    h['X-Spider-Run-ID'] = item['spider_run_id']
    # XXX Scrapy doesn't provide remote IP for WARC-IP-Address

    # below based on WARCRecord.from_response()

    # XXX scrapy doesn't provide human-readable status string
    status = "HTTP/1.1 {} {}".format(item['status'],
                                     httpstatus.HTTPStatus(item['status']).name).encode()
    headers = [b': '.join((k, v)) for k, l in item['headers'].items() for v in l]

    record.update_payload(b"\r\n".join(itertools.chain((status, ),
                                                       headers,
                                                       (b'', ),
                                                       (item['content'], )
                                                       )))

def update_warc_metadata_from_item(record, item):
    """update a WARC metadata record from a scrapy Item"""

    # make empty header object to use for fields
    # XXX WARCHeader messes up capitalization here
    fields = warc.WARCHeader({}, defaults=False)
    fields['x-crawl-depth'] = item['depth']
    fields['hopsFromSeed'] = item['hops_from_seed']
    fields['x-source-anchor'] = item['source_anchor']
    fields['x-source-url'] = item['source_url']

    buf = BytesIO()
    fields.write_to(buf, version_line=False, extra_crlf=False)
    record.update_payload(buf.getvalue())

class WarcStorePipeline(object):
    """Stores web pages in WARC files, similar to `FilesPipeline`.

    Saves to a filesystem or S3 path specified in the `FILES_STORE` setting.
    Pages will be named `<spider>run_id>/<warc-id>.warc`, with a `response`
    and `metadata` records.

    We piggyback on WarcFilesPipeline below, which uses singleton classes for S3/FS
    storage.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, store_uri):
        if not store_uri:
            raise NotConfigured

        self.store = self._get_store(store_uri)

    def open_spider(self, spider):
        # write a warcinfo WARC for this spider run
        record = new_warc('warcinfo')
        update_warc_info_from_spider(record, spider)
        path = path_from_warc(record, spider.run_id)
        buf = BytesIO()
        record.write_to(buf)
        self.store.persist_file(path, buf, None)

    @classmethod
    def from_crawler(cls, crawler):
        pipe = cls(crawler.settings['FILES_STORE'],)
        pipe.crawler = crawler
        return pipe

    @staticmethod
    def _get_store(uri):
        # ripped from FilesPipline
        if os.path.isabs(uri):  # to support win32 paths like: C:\\some\dir
            scheme = 'file'
        else:
            scheme = urlparse(uri).scheme
        store_cls = FilesPipeline.STORE_SCHEMES[scheme]
        return store_cls(uri)

    def process_item(self, item, spider):
        # calculate metadata
        item["length"] = len(item["content"])
        item["spider_name"] = spider.name
        item["spider_revision"] = git_revision
        item["spider_parameters"] = spider.get_parameters()
        item["spider_run_id"] = spider.run_id
        item["retrieved"] = int(time.time())

        # make a WARC Record
        record = new_warc('response')
        update_warc_response_from_item(record, item)

        # make a WARC metadata
        metadata = new_warc('metadata')
        update_warc_metadata_from_item(metadata, item)
        metadata.header['WARC-Concurrent-To'] = record.header.record_id

        # write it all out
        path = path_from_warc(record, spider.run_id)
        buf = BytesIO()
        record.write_to(buf)
        metadata.write_to(buf)
        self.store.persist_file(path, buf, None)
        return item
