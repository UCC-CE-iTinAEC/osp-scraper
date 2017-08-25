import os
import urllib

from twisted.trial import unittest
import warc

from osp_scraper.tasks import crawl

class ServerTestCase(unittest.TestCase):
    """Tests the osp_scraper_spider by running it on a test server.

    It then checks the WARC files generated to see if their metadata
    matches the expected values.

    To run it, first start the Flask server with:
        $ python tests/app/test_server.py
    Then run the tests with:
        $ trial tests.server_tests
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warc_metadata_by_path = {}

    def setUp(self):
        crawl(
            'osp_scraper_spider',
            start_urls=["http://127.0.0.1:5000/start_path/"]
        )

        crawl_dir, = os.listdir("downloads/")
        for filename in os.listdir("downloads/" + crawl_dir):
            with warc.open(f"downloads/{crawl_dir}/{filename}") as warc_file:
                records = list(warc_file)
            if len(records) == 2:
                response_record, metadata_record = records

                url = response_record['WARC-Target-URI']
                u = urllib.parse.urlparse(url)
                path = u.path

                metadata_payload = metadata_record.payload.getvalue()\
                    .decode("utf-8")\
                    .strip()

                metadata = {}
                for line in metadata_payload.split("\r\n"):
                    key, value = line.split(": ")
                    metadata[key] = value

                self.warc_metadata_by_path[path] = metadata

    def test_start_url(self):
        metadata = self.warc_metadata_by_path["/start_path/"]

        self.assertEqual(metadata["X-Crawl-Depth"], "0")
        self.assertEqual(metadata["Hopsfromseed"], "0")
        self.assertEqual(metadata["X-Source-Anchor"], "None")
        self.assertEqual(metadata["X-Source-Url"], "None")
