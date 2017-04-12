# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SFASUSpider(CustomSpider):
    """
    This site requires a viewstate to be passed with every POST request.
    Unfortunately, the viewstate on the first page is approximately 1MB in size
    and including it in a request causes the request to time out, maybe due to a
    bug in Scrapy or Twisted.  As a workaround, the scraper uses a smaller
    viewstate from a different page.
    """

    name = "sfasu"

    start_urls = ["https://orion.sfasu.edu/courseinformation/"]

    def parse(self, response):
        for option in response.css("select option"):
            code = option.css("::attr(value)").extract_first()
            if code:
                name = option.css("::text").extract_first()
                yield scrapy.FormRequest.from_response(
                    response,
                    formdata={
                        '__VIEWSTATE': "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MU0vU09DMTM5MS5wZGY/NjM2MjU1MzkyMjgxOTQwMDIxHwdlZGQCAw8PFgYfAwUHMTM5LjAwMR8HZR8AaGRkAgEPZBYGAgEPDxYEHwMFFkRFTlRJQ0UsIERJQU5ORSBFSUxFRU4fBgUffi9jdi82MjEucGRmPzYzNjI1NTM5MjI4MTk0MDAyMWRkAgMPDxYEHwMFFkRFTlRJQ0UsIERJQU5ORSBFSUxFRU4fAGhkZAIEDxUDAzYyMQNjcjEWREVOVElDRSwgRElBTk5FIEVJTEVFTmQCAg8PFgIfAGhkZBghBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxOSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyMSRHcmlkVmlldzEPPCsADAEIAgFkBTRjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJEZvcm1WaWV3QWN0aXZlDxQrAAdkZGRkZBYAAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxNyRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxNiRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwNyRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwNSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxNCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwMSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyNSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxOCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwOSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwzMiRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwzMCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxMyRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxMSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyNyRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyMCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyOCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwMiRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwNiRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwNCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwOCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyOSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyMiRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyMyRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwwMyRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxMiRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxMCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyNiRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwyNCRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwxNSRHcmlkVmlldzEPPCsADAEIAgFkBT9jdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHRlcm1yZXBvcnQxJFJlcGVhdGVyMSRjdGwzMSRHcmlkVmlldzEPPCsADAEIAgFki//sDXgO0ZCk9D8kF+MKRjx+2CuHQ8RMjnZNPHNApyY=",
                        '__VIEWSTATEGENERATOR': "D51B1D6E",
                        '__EVENTVALIDATION': "/wEdACUnRauzksqTZx4sIQZZCyM8SsCoeH9rlU5VXvu4GEag9m4hIMn/BRov5wz/U7j3Ud4gw1e5DHcv5nwE6PPf2i2FdBkipPmiBQePS4tN0+GiEzq0Lt/LDcdnpr7RMK7XN3J8ch9x72NWatbVt4+SsqxmK1dhVzI8ZqdVYawSDYZLBejRGBikyXWrUvnVs9cfQOivAhVof+Rlfxlg4yxy7Bcmz4ZSnxSnu4LfRHbgiJZ9+RBjGKbffHcu8UjWmXDvvblp6JJ3RofLue6RvL50Uonv99f50Flmjp4pAS7QhMN8Pcw6bait6l29j0loTiKNNX1O04G4znTpbQg0c2CUp8KoWX9vjJ1rPxGzTH/w1mK06yaQ8xdvTA1q8QYz5ggvPtX15eZxwQnOcJBKdarfk9g/j87LKYei97TWB+tAuvb/EoYqiR4wuqd7drHwaxie9NCcTs/0uZkqBgEQkYw+RaViTKj5JRRxUSCEOiTuj+kOu4HUZpFmE00hYkSfpgkp5Wb0FYVW5xz1vwacc84usQ47NHtNrk7yrophe1kJMxNLvYadQmkTnSxxyK7KqA6Jn1KI03ws8NjVtGfUAv2js4Sy5UQIHrRxwWJlGtnOpTsB7L8wk8KhNHCfs32Wh1KSn7YSxryDh2naAvc4M7Hf9ueskIIn9SlVm2W/L+bWbvJTHJISeSWLf62iY2XaNDlWddmuZBIjJVasUXFNzrwL7Qz28HcpCQlzrFxRWc0MXmLGyOg0NnCP5ztfU0Zql2f54zG6EUbF9In9hIIBlNp0zjPEcS+e8XOt42s92wZdiJ6jJWcP12ku5g+YUZKRXk+axZM=",
                        'ctl00$ContentPlaceHolder1$termreport1$DropDownListTerm': code
                    },
                    meta={
                        'source_url': response.url,
                        'source_anchor': name,
                        'depth': 1,
                        'hops_from_seed': 1
                    },
                    callback=self.parse_for_files
                )

    def extract_links(self, response):
        for a_tag in response.css(".section-dark tr td:first-child a"):
            relative_url = a_tag.css("::attr(href)").extract_first()
            a_text = a_tag.css("::text").extract()
            a_title = a_tag.css("::attr(title)").extract()
            url = response.urljoin(relative_url)
            # Some links don't have a title
            anchor = " ".join(a_text + a_title)
            yield (url, anchor)