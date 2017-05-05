# -*- coding: utf-8 -*-

from io import BytesIO

import PyPDF2 as pyPdf
import scrapy

from ..spiders.CustomSpider import CustomSpider

class PDFSpider(CustomSpider):
    """
    This scraper can download files that are linked from a PDF.  It will extract
    every single link from the PDF and yield a PageItem for each PDF, with the
    links as file_urls.
    """
    name = "pdf"

    def start_requests(self):
        for start_url in self.database_urls:
            yield scrapy.Request(
                start_url,
                meta={
                    'depth': 0,
                    'hops_from_seed': 0,
                    'source_url': start_url,
                    'source_anchor': start_url
                },
                callback=self.parse
            )

    def parse(self, response):
        for item in self.parse_for_files(response):
            yield item

    def extract_links(self, response):
        pdf = pyPdf.PdfFileReader(BytesIO(response.body))
        pgs = pdf.getNumPages()

        for page_num in range(pgs):
            page = pdf.getPage(page_num)

            annotations = page.get('/Annots', [])
            for annotation in annotations:
                annot_object = annotation.getObject()

                a_tag = annot_object.get('/A')
                if a_tag and '/URI' in a_tag:
                    uri = a_tag['/URI']
                    if isinstance(uri, pyPdf.generic.ByteStringObject):
                        uri = uri.decode("utf-8").replace("\x00", "")
                    yield (uri, uri)
