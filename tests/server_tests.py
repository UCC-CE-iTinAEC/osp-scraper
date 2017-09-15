import os
import shutil
import urllib

import unittest
import warc

from osp_scraper.tasks import crawl

HOST = "http://127.0.0.1:5000"

class ServerTestCase(unittest.TestCase):
    """Tests the osp_scraper_spider by running it on a test server.

    It then checks the WARC files generated to see if their metadata
    matches the expected values.

    To run it, first start the Flask server with:
        $ python tests/app/test_server.py
    Then run the tests with:
        $ python -m unittest tests/server_tests.py
    """

    warc_metadata_by_path = {}

    @classmethod
    def setUpClass(cls):
        FILES_DIR = "_unittest_temp"
        os.environ["FILES_STORE"] = f"file://{FILES_DIR}/"
        os.environ["DOWNLOAD_DELAY"] = "0"
        os.environ["LOG_LEVEL"] = "DEBUG"

        if os.path.isdir(FILES_DIR):
            shutil.rmtree(FILES_DIR)

        crawl(
            'osp_scraper_spider',
            start_urls=[
                f"{HOST}/path/0/",
                f"{HOST}/start_path/",
            ],
            max_hops_from_seed=10
        )

        crawl_dir, = os.listdir(FILES_DIR)
        for filename in os.listdir(f"{FILES_DIR}/{crawl_dir}"):
            with warc.open(f"{FILES_DIR}/{crawl_dir}/{filename}") as warc_file:
                records = list(warc_file)
            if len(records) == 2:
                response_record, metadata_record = records

                url = response_record['WARC-Target-URI']
                relative_url = url.replace(HOST, "")

                metadata_payload = metadata_record.payload.getvalue()\
                    .decode("utf-8")\
                    .strip()

                metadata = {}
                for line in metadata_payload.split("\r\n"):
                    key, value = line.split(": ")
                    metadata[key] = value

                cls.warc_metadata_by_path[relative_url] = metadata

    def test_start_url(self):
        self.assertIn("/start_path/", self.warc_metadata_by_path)

        metadata = self.warc_metadata_by_path["/start_path/"]

        self.assertEqual(metadata["X-Crawl-Depth"], "0")
        self.assertEqual(metadata["Hopsfromseed"], "0")
        self.assertEqual(metadata["X-Source-Anchor"], "None")
        self.assertEqual(metadata["X-Source-Url"], "None")

    def test_anchor(self):
        metadata = self.warc_metadata_by_path["/"]
        self.assertEqual(metadata["X-Source-Anchor"], "link to /")

    def test_source_url(self):
        metadata = self.warc_metadata_by_path["/"]
        self.assertEqual(metadata["X-Source-Url"], f"{HOST}/start_path/")

    def test_depth_on_path(self):
        self.assertEqual(
            self.warc_metadata_by_path["/path/0/infinite/1"]["X-Crawl-Depth"],
            "0"
        )
        self.assertEqual(
            self.warc_metadata_by_path["/path/0/infinite/10"]["X-Crawl-Depth"],
            "0"
        )

    def test_depth_off_path(self):
        self.assertEqual(
            self.warc_metadata_by_path["/path/1/"]["X-Crawl-Depth"],
            "1"
        )
        self.assertEqual(
            self.warc_metadata_by_path["/path/2/"]["X-Crawl-Depth"],
            "2"
        )

    def test_pdf_file(self):
        self.assertIn("/path/0/file/fileA.pdf", self.warc_metadata_by_path)

    def test_doc_file(self):
        self.assertIn("/path/0/file/fileA.doc", self.warc_metadata_by_path)

    def test_docx_file(self):
        self.assertIn("/path/0/file/fileA.docx", self.warc_metadata_by_path)

    def test_rtf_file(self):
        self.assertIn("/path/0/file/fileA.rtf", self.warc_metadata_by_path)

    def test_max_depth(self):
        self.assertIn("/path/2/", self.warc_metadata_by_path)
        self.assertNotIn("/path/3/", self.warc_metadata_by_path)

    def test_max_hops_from_seed(self):
        self.assertIn("/path/0/infinite/1", self.warc_metadata_by_path)

        self.assertIn("/path/0/infinite/10", self.warc_metadata_by_path)
        self.assertNotIn("/path/0/infinite/11", self.warc_metadata_by_path)

    def test_redirected_file(self):
        path = "/path/0/redirect?url=/path/0/file/redirected_file.pdf"
        self.assertIn(path, self.warc_metadata_by_path)
        metadata = self.warc_metadata_by_path[path]
        self.assertEqual(metadata["X-Crawl-Depth"], "0")
        self.assertEqual(metadata["Hopsfromseed"], "1")

    def test_redirect_to_off_path_page(self):
        path = "/off_path/0/redirected?redirected_from=on_path"
        self.assertIn(path, self.warc_metadata_by_path)
        metadata = self.warc_metadata_by_path[path]
        self.assertEqual(metadata["X-Crawl-Depth"], "0")
        self.assertEqual(metadata["Hopsfromseed"], "1")

    def test_redirect_to_on_path_page(self):
        path = "/path/0/redirected?redirected_from=on_path"
        self.assertIn(path, self.warc_metadata_by_path)
        metadata = self.warc_metadata_by_path[path]
        self.assertEqual(metadata["X-Crawl-Depth"], "0")
        self.assertEqual(metadata["Hopsfromseed"], "1")

    def test_iframe(self):
        self.assertIn(
            "/path/0/iframe?url=/path/0/iframe_embedded",
            self.warc_metadata_by_path
        )
        self.assertIn("/path/0/iframe_embedded", self.warc_metadata_by_path)

    def test_frame(self):
        self.assertIn(
            "/path/0/frame?url=/path/0/frame_embedded",
            self.warc_metadata_by_path
        )
        self.assertIn("/path/0/frame_embedded", self.warc_metadata_by_path)

    def test_off_domain_depth(self):
        self.assertIn(
            "http://httpbin.org/html?source_path=0",
            self.warc_metadata_by_path
        )

        self.assertNotIn(
            "http://httpbin.org/html?source_path=1",
            self.warc_metadata_by_path
        )

