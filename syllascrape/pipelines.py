# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.utils.python import to_bytes

import hashlib
import os.path
import time
from io import BytesIO

from . import items
from .utils import extract_domain

class WebStorePipeline(object):
    """Stores web pages, similar to `FilesPipeline`.

    Saves to a filesystem or S3 path specified in the `FILES_STORE` setting.
    Pages will be named `html/<url_hash>-<epoch>.html`, with an accompanying
    `.json` file containing metadata.

    We piggyback on WebFilesPipeline below, which uses singleton classes for S3/FS
    storage.
    """

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

    @staticmethod
    def file_path(item):
        """given an item, return the base name of a file it can be saved to"""
        url_hash = hashlib.md5(to_bytes(item["url"])).hexdigest()
        return 'html/{:s}-{:d}'.format(url_hash, item['retrieved'])

    def process_item(self, item, spider):
        # calculate metadata
        item["domain"] = extract_domain(item["url"])
        item["checksum"] = hashlib.md5(to_bytes(item["content"])).hexdigest()
        item["length"] = len(item["content"])
        item["spider"] = spider.version_string
        item["retrieved"] = int(time.time())

        # XXX source_url & provenance?

        path = self.file_path(item)

        # save the raw bytes
        self.store.persist_file("%s.html" % path, BytesIO(item["content"]), None)

        # jsonify the item's metadata
        json_buf = BytesIO(self.encoder.encode({k:v for k, v in item.items() if k != 'content'}).encode('utf-8'))
        self.store.persist_file("%s.json" % path, json_buf, None)

        return item

class WebFilesPipeline(FilesPipeline):
    """A customized `FilesPipeline`

    Saves to a filesystem or S3 path specified in the `FILES_STORE` setting.
    Pages will be named `<ext>/<url_hash>-<epoch>.<ext>`, with an accompanying
    `.json` file containing metadata.

    This subclass effectively bypasses the `FILES_EXPIRES` setting; files
    will be downloaded anew each time they are encountered.
    """

    def __init__(self, *args, **kwargs):
        self.encoder = ScrapyJSONEncoder()
        super().__init__(*args, **kwargs)

    def item_completed(self, results, item, info):
        # callback executed when all files for an item have been downloaded
        super().item_completed(results, item, info)

        for d in item.get(self.files_result_field, ()):
            i = items.FileItem()
            i["url"] = d["url"]
            i["domain"] = extract_domain(d["url"])
            i["checksum"] = d["checksum"]
            i["retrieved"] = d["retrieved"]
            i["spider"] = info.spider.version_string
            i["source_url"] = item["url"]
            i["provenance"] = item["provenance"]

            path = os.path.splitext(d['path'])[0]
            json_buf = BytesIO(self.encoder.encode(i))
            self.store.persist_file("%s.json" % path, json_buf, None)

        return item

    def media_downloaded(self, response, request, info):
        # hook called after each file is downloaded

        # stuff timestamp on the response so we can use it in `file_path` below
        response.retrieved = int(time.time())

        # the dictionary here ends up in `item[file_results_field]` above
        d = super().media_downloaded(response, request, info)
        d["retrieved"] = response.retrieved
        d["length"] = len(response.body)
        return d

    def file_path(self, request, response=None, info=None):
        # hook to generate file name. This does something slightly evil - by
        # including the timestamp in the filename, we force the file to be
        # downloaded anew each time because the call to
        # `FilesStore.stat_file(..)` will 404.

        url_hash = hashlib.md5(to_bytes(request.url)).hexdigest()
        ext = os.path.splitext(request.url)[1].lower()
        retrieved = getattr(response, 'retrieved', 0)
        return '{:s}/{:s}-{:d}{:s}'.format(ext[1:], url_hash, retrieved, ext)