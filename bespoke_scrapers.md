# Writing bespoke scrapers
We're standardizing on [Scrapy](http://scrapy.org) as a platform from crawling & data ingest (so we only need to write data storage once). We collect raw bytes of the web pages in this phase; finding the syllabi among them & extracting data is a later step in the pipeline

## Getting Started
[Docs for Scrapy](https://doc.scrapy.org/en/latest/) ; please use python 3.4 or 3.5. When you're writing scrapers, use Scrapy's CSS selectors instead of XPath, it's much easier.

Make sure to set `HTTPCACHE_ENABLED = True` and `DOWNLOAD_DELAY = 5.0` in your local scrapy settings so it doesn't consume the earth.

## Writing spiders

You should generate `PageItems` like those in the the [existing crawler](https://github.com/wearpants/syllascrape/blob/master/syllascrape/items.py)

You can import the syllascrape package into your spider & use that class directly if you like, but don't try to write your code inside Syllascrape though, it's a bit customized.

You can use Scrapy's `FormRequest` to [submit forms](https://doc.scrapy.org/en/latest/topics/request-response.html#formrequest-objects). The goal is want to extract a list of items from 2-3 fields, and the crawl all possible combinations by submitting the form. There are `product()` and `permutation()` functions in the Python `itertools` library if you want to use them.

