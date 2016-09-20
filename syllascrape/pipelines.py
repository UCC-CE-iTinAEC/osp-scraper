# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes
from scrapy.utils.misc import md5sum

import warc

import uuid
import logging
import hashlib
import os.path
import time
import json
import itertools
from io import BytesIO
from urllib.parse import urlparse

from . import items
from .utils import extract_domain, file_path, guess_extension
from .version import git_revision

def path_from_warc(record, prefix=""):
    """return a path from the Record ID of a WARC"""
    path = "%s.warc" % record.header.record_id[10:-1]
    return os.path.join(prefix, path)

def new_warc():
    """return a new WARCRecord"""

    # ripped from WARCHeader.init_defaults()
    headers = {

        'WARC-Record-ID': "<urn:uuid:%s>" % uuid.uuid1(),
        'Content-Type': 'application/http; msgtype=response',
    }

    return warc.WARCRecord(header=warc.WARCHeader(headers, defaults=False),
                           defaults=False)

def update_warc_from_item(record, item):
    """update a WARC record from a scrapy Item"""
    h = record.header
    h['WARC-Target-URI'] = item['url']
    h['WARC-Date'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(item['retrieved']))
    # XXX Scrapy doesn't provide remote IP for WARC-IP-Address

    # XXX these should go in a WARC metadata record
    h['X-Spider-Name'] = item['spider_name']
    h['X-Spider-Revision'] = item['spider_revision']
    h['X-Crawl-Depth'] = item['depth']
    h['X-Hops-From-Seed'] = item['hops_from_seed']

    # XXX this should go in a single WARC warcinfo record, not each response
    h['X-Spider-Parameters'] = json.dumps(item['spider_parameters'])
    h['X-Spider-Run-ID'] = item['spider_run_id']

    # below based on WARCRecord.from_response()

    # XXX scrapy doesn't provide human-readable status string
    status = "HTTP/1.1 {} UNKNOWN".format(item['status']).encode()
    headers = [b': '.join((k, v)) for k, l in item['headers'].iteritems() for v in l]

    record.update_payload(b"\r\n".join(itertools.chain((status, ),
                                                       headers,
                                                       (b'', ),
                                                       (item['content'], )
                                                       )))

class WarcStorePipeline(object):
    """Stores web pages, similar to `FilesPipeline`.

    Saves to a filesystem or S3 path specified in the `FILES_STORE` setting.
    Pages will be named `<ext>/<url_hash>-<epoch>.<ext>`, with an accompanying
    `.json` file containing metadata.

    We piggyback on WebFilesPipeline below, which uses singleton classes for S3/FS
    storage.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, store_uri):
        if not store_uri:
            raise NotConfigured

        self.store = self._get_store(store_uri)

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
        item["domain"] = extract_domain(item["url"])
        item["checksum"] = hashlib.md5(to_bytes(item["content"])).hexdigest()
        item["length"] = len(item["content"])
        item["spider_name"] = spider.name
        item["spider_revision"] = git_revision
        item["spider_parameters"] = spider.get_parameters()
        item["spider_run_id"] = spider.run_id
        item["retrieved"] = int(time.time())

        # make a WARC Record
        record = new_warc()
        update_warc_from_item(record, item)

        # write it out
        path = path_from_warc(record, spider.run_id)
        buf = BytesIO()
        record.write_to(buf)
        self.store.persist_file(path, buf, None)
        return item

class WarcFilesPipeline(FilesPipeline):
    """A customized `FilesPipeline`

    Saves to a filesystem or S3 path specified in the `FILES_STORE` setting.
    Files will be named `<ext>/<url_hash>-<epoch>.<ext>`, with an accompanying
    `.json` file containing metadata.

    This subclass effectively bypasses the `FILES_EXPIRES` setting; files
    will be downloaded anew each time they are encountered.

    `FILES_URLS_FIELD` should be a list of 2 tuples of `(url, meta)`, where
    the second item is a dict to pass as metadata to `scrapy.Request`.
    """

    logger = logging.getLogger(__name__)

    def get_media_requests(self, item, info):
        # hook to generate requests. We expect files_urls_field to be a list of 2 tuples of (url, meta)
        return [scrapy.Request(url, meta=meta) for url, meta in item.get(self.files_urls_field, [])]

    def file_downloaded(self, response, request, info):
        # hook called to write bytes
        path = self.file_path(request, response=response, info=info)

        # build a a scrapy Item for this file
        i = items.PageItem()
        i["url"] = request.url
        i["domain"] = extract_domain(i["url"])
        i["retrieved"] = int(time.time())
        i["content"] = response.body
        i["length"] = len(response.body)
        i["headers"] = response.headers
        i["status"] = response.status
        i["source_anchor"] = response.meta["source_anchor"]
        i["source_url"] = response.meta["source_url"]
        i["depth"] = response.meta["depth"]
        i["hops_from_seed"] = response.meta["hops_from_seed"]
        i["spider_name"] = info.spider.name
        i["spider_revision"] = git_revision
        i["spider_parameters"] = info.spider.get_parameters()
        i["spider_run_id"] = info.spider.run_id

        # update WARC record
        record = response.meta["warc_record"]
        update_warc_from_item(record, i)

        buf = BytesIO()
        record.write_to(buf)
        checksum = md5sum(buf)
        buf.seek(0)
        self.store.persist_file(path, buf, info)
        return checksum

    def file_path(self, request, response=None, info=None):
        # hook to generate file name. This does something slightly evil - by
        # generating a unique filename, we force the file to be downloaded
        # anew each time because the call to `FilesStore.stat_file(..)` will
        # 404.

        # Make a WARC Record *here*, and use it's `header.record_id` for the file_path
        # Stuff record on the response object, pull it off in media downloaded & stuff it in return dict
        # Read record off dict in item_completed, write to file path using the `record_id` above

        assert info is not None

        if response is None:
            # this happens in FilesPipeline.media_to_download to check if
            # file already exists in storage. We just generate a throwaway
            # path, forcing it to always be downloaded
            record = new_warc()
        elif 'warc_record' not in response.meta:
            # first time file_path has been called for this response
            record = new_warc()
            response.meta['warc_record'] = record
        else:
            # we've been called before for this response, returing existing record
            record = response.meta['warc_record']

        return path_from_warc(record, info.spider.run_id)