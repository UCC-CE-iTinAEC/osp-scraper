# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes

import warc

import logging
import hashlib
import os.path
import time
from io import BytesIO
from urllib.parse import urlparse

from . import items
from .utils import extract_domain, file_path, guess_extension
from .version import git_revision


def build_record():
    # make a WARC Header
    header = warc.WARCHeader(headers={"WARC-Type": "resource"},
                             defaults=True)

    return header


class WebStorePipeline(object):
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
        self.encoder = ScrapyJSONEncoder()

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
        item["retrieved"] = int(time.time())


        # make a WARC Record
        record = warc.WARCRecord(payload=item["content"],
                                 headers={"WARC-Type": "resource"},
                                 defaults=True)


        path = 'warc/%s.warc' % record.header.record_id
        buf = BytesIO()
        record.write_to(buf)
        self.store.persist_file(path, buf, None)
        return item

class WebFilesPipeline(FilesPipeline):
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

    def __init__(self, *args, **kwargs):
        self.encoder = ScrapyJSONEncoder()
        super().__init__(*args, **kwargs)

    def get_media_requests(self, item, info):
        # hook to generate requests. We expect files_urls_field to be a list of 2 tuples of (url, meta)
        return [scrapy.Request(url, meta=meta) for url, meta in item.get(self.files_urls_field, [])]

    def item_completed(self, results, item, info):
        # callback executed when all files for an item have been downloaded
        super().item_completed(results, item, info)

        for d in item.get(self.files_result_field, ()):
            i = items.FileItem()
            i["url"] = d["url"]
            i["domain"] = extract_domain(d["url"])
            i["checksum"] = d["checksum"]
            i["retrieved"] = d["retrieved"]
            i["source_anchor"] = d["source_anchor"]
            i["spider_name"] = info.spider.name
            i["spider_revision"] = git_revision
            i["spider_parameters"] = info.spider.get_parameters()
            i["source_url"] = item["url"]

            # XXX much of this needs to be made available in file_downloaded!

        return item

    def media_downloaded(self, response, request, info):
        # hook called after each file is downloaded

        # stuff timestamp on the response so we can use it in `file_path` below
        response.retrieved = int(time.time())

        # the dictionary here ends up in `item[file_results_field]` above
        d = super().media_downloaded(response, request, info)
        d["retrieved"] = response.retrieved
        d["length"] = len(response.body)
        d["source_anchor"] = response.meta["source_anchor"]
        d["depth"] = response.meta["depth"]
        d["warc_header"] = response.meta["warc_header"]
        d["warc_record"] = response.meta["warc_record"]
        return d

    def file_downloaded(self, response, request, info):
        # hook called to write bytes
        path = self.file_path(request, response=response, info=info)

        # make a WARC record
        record = response.meta["warc_record"] = warc.WARCRecord(header=response.meta["warc_header"],
                                                                payload=response.bytes,
                                                                defaults=True)
        buf = BytesIO()
        record.write_to(buf)
        checksum = md5sum(buf)
        buf.seek(0)
        self.store.persist_file(path, buf, info)
        return checksum

    def file_path(self, request, response=None, info=None):
        # hook to generate file name. This does something slightly evil - by
        # including the timestamp in the filename, we force the file to be
        # downloaded anew each time because the call to
        # `FilesStore.stat_file(..)` will 404.

        # XXX Make a WARC Header *here*, use `file_data/<header.record_id>.dat` for the file_path
        # Stuff header on the response object, pull it off in media downloaded & stuff it in return dict
        # Read header off dict in item_completed, write a WARC Record using the `record_id` above
        # Side job to concat WARCs will inline .dat file & write a new WARC Header

        if response is None:
            # this happens in FilesPipeline.media_to_download to check if
            # file already exists in storage. We just generate a throwaway
            # path, forcing it to always be downloaded
            header = build_header()
        elif 'warc_header' not in response.meta:
            # first time file_path has been called for this response
            header = build_header()
            response.meta['warc_header'] = header
        else:
            # we've been called before for this response, returing existing header
            header = response.meta['warc_header']

        return 'data/%s.dat' % header.record_id