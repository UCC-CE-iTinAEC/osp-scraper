# Writing Custom Scrapers

We use [Scrapy 1.4.0](https://doc.scrapy.org/en/1.4/) for writing web crawlers
that scrape syllabi.  This document will not be a comprehensive breakdown of
everything that goes into scraping syllabi; instead, it will focus on
information relevant to working with the
[osp-scraper](https://github.com/opensyllabus/osp-scraper) project.  For
best results, consider this document alongside the official Scrapy
documentation.  Links to specific topics will be provided when appropriate.

## Motivation
Bulk web scraping is handled by invoking the
[`FilterSpider`](../osp_scraper/spiders/__init__.py) on sets of URLs.
`FilterSpider` will recursively follow links embedded in HTML pages, constrained
by a set of filters that prevent it from crawling infinitely or breaking out of
the path of the original URL it was given.  However, `FilterSpider` has two key
limitations:

- It cannot complete forms.
- It can only make GET requests, not POST requests.

When scraping a set of syllabi requires either of these two things, we create
custom scripts tailored to the specific sites or frameworks in question.

## Custom Scrapers
All scrapers inherit from the
[`CustomSpider`](../osp_scraper/spiders/CustomSpider.py) class.  The outline for
writing custom scrapers is as follows:

- Give the scraper a unique name.
- Define a list of `start_urls` or configure the scraper to work with
  `self.database_urls`.
- Implement either `parse` (preferred) or `start_requests`.
- Create requests with each `callback` set to pass responses from method to
  method, leading the scraper to the point where it can scrape syllabi.
- Set `meta` content and have the final `callback` be to `parse_for_files`.
  Define an `extract_links` method if appropriate.

Details are provided below.

### Getting started
All names of scrapers are based on either the hostname, if the scraper is for a
single site (e.g, [utexas](../osp_scraper/spiders/utexas.py)), or the framework
name, if the scraper is targeting a general framework (e.g,
[campusconcourse](../osp_scraper/spiders/campusconcourse.py)).  For name
'myname', work is done off a git branch named `scraper/myname` and in a file
`myname.py`, saved in [`osp_scraper/spiders`](../osp_scraper/spiders).  The top
of each custom scraper file should look similar to this:

```python
# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class MyNameSpider(CustomSpider):
	name = "myname"
```

### Start URLs
If a scraper targets a single site, define a list of `start_urls` containing all
URL strings that are necessary to start the scraping process for that site.
Most of the time, `start_urls` will contain a single URL.

If a scraper targets a framework that is used across multiple sites, instead use
`self.database_urls` URLs in a `start_requests` method (described below).  The
`self.database_urls` field is supplied by the
[`edu_repo_crawler.py`](../bin/edu_repo_crawler.py) script, and is populated by
URLs from the `Database URLs` column in a CSV file.

Note that we don't bother defining a list of `allowed_domains` for custom
scrapers, since custom scrapers are meant for highly targeted scraping anyway.

### Choosing `parse` or `start_requests`
Most of the time, `parse` will be the first method defined in each custom
scraper.  The `parse` method is the default `callback` for all Scrapy requests,
and is automatically fed the response objects from making `scrapy.Request` calls
to the URLs in `start_urls`.

If this behavior is not desireable, or if `self.database_urls` is being used, it
may be helpful to implement `start_requests` instead and manually iterate over a
list of URLs.  An example of this can be found in
[`campusconcourse.py`](../osp_scraper/spiders/campusconcourse.py).

For more details about the relationship between `parse` and `start_requests`,
see the [Scrapy
documentation](https://doc.scrapy.org/en/1.4/intro/tutorial.html).

### Requests and Chaining Callbacks
There are three types of requests used by the custom scrapers:

- `scrapy.Request`: Used to make basic HTTP requests.  Whenever possible, make
  use of
  [`response.follow`](https://doc.scrapy.org/en/1.4/topics/request-response.html#scrapy.http.TextResponse.follow).
- `scrapy.FormRequest`: An HTTP request that can complete forms and send data
  via a `formdata` dictionary.
- `scrapy.FormRequest.from_response`: Takes as input a `response` object and
  creates a `FormRequest` populated with elements found in an HTML `<form>`.
  Can lead to unexpected behavior.

For more details, see the [Scrapy
docs](https://doc.scrapy.org/en/1.4/topics/request-response.html).

When making form requests, use `scrapy.FormRequest.from_response` whenever it is
appropriate and functional, and `scrapy.FormRequest` otherwise.  When non-form
requests are necessary, always use `response.follow` as a shortcut if it is
appropriate.  Otherwise, use `scrapy.Request`.  For details on using
`response.follow` as a shortcut, see
[here](https://doc.scrapy.org/en/1.4/intro/tutorial.html#response-follow-example).

Organize the arguments of a Scrapy requests similar to how an HTTP request is
organized.  Arguments should go in this order:

- The `response` object, if using `scrapy.FormRequest.from_response`, and the
  URL string otherwise.
- The `formname`, `formid`, or `formcss` if using `FormRequest.from_response`
  and the response contains multiple forms.
- A `method="POST"` setting, if the request is a POST request.  Also, when using
  `FormRequest`, a `method="GET"` setting, as needed.
- A `headers` dictionary, if needed (this is uncommon).
- A `formdata` dictionary, if making a form request.
- A `meta` dictionary, as needed.
- A `dont_click=True` setting, if doing a form request and a form is submitted
  without a button click (this is uncommon).  See the [Scrapy
  docs](https://doc.scrapy.org/en/1.4/topics/request-response.html#formrequest-objects)
  for more information.
- A `callback` to another method.

Any other arguments required to make the request should be inserted towards the
end of the list of arguments, but before the `callback`.  The `callback` should
always be the final argument.

The default `method` for `scrapy.Request` is `"GET"`, and the default `method`
for `scrapy.FormRequest` is `"POST"`.  When calling
`scrapy.FormRequest.from_response`, Scrapy will try to determine the `method`
from the `response` object.  Always specify `method="POST"` when making a POST
request.  Sometimes, when using `scrapy.FormRequest`, it may be necessary to set
`method="GET"`.  Do not specify `method="GET"` when it is not necessary.

Here's an example of a request from
[`inverhills.py`](../osp_scraper/spiders/inverhills.py):

```python
yield scrapy.FormRequest.from_response(
	response,
	formid="form1",
	method="POST",
	formdata={
		'cboTerm': term_code,
		'cboSubject': subject_code
	},
	meta={
		'depth': 1,
		'hops_from_seed': 1,
		'source_url': response.url,
		'source_anchor': term_name + " " + subject_name
	},
	callback=self.parse_for_files
)
```

### Generating `PageItem` objects
The ultimate goal behind each custom scraper is to execute a sequence of
requests up to the point where links to syllabi are available.  Then, `PageItem`
objects are made out of the link, relevant `meta` dictionaries and `response`
object fields.  Each `PageItem` is saved as part of a WARC archive, which is
later fed through the item pipeline (see the
[osp-pipeline](https://github.com/opensyllabus/osp-pipeline) repository)

Each `PageItem` should always be generated by a `callback` to `parse_for_files`,
which is a method available in the
[`CustomSpider`](../osp_scraper/spiders/CustomSpider.py) class, as in the
[`inverhills.py`](../osp_scraper/spiders/inverhills.py) example above.  The
`parse_for_files` method will `yield` a `PageItem` like this:

```python
yield PageItem(
	url=response.url,
	content=response.body,
	headers=response.headers,
	status=response.status,
	source_url=response.meta['source_url'],
	source_anchor=self.clean_whitespace(response.meta['source_anchor']),
	depth=response.meta['depth'],
	hops_from_seed=response.meta['hops_from_seed'],
	file_urls=file_urls
)
```

Most of the values come from the `response` object handed to `parse_for_files`
on `callback`.  Note that the following `meta` fields need to be set in the
request:

- `depth` and `hops_from_seed`: A number representing the "distance traveled"
  (usually number of requests made) from the initial URL.  Start counting at 0.
- `source_url`: The URL that the syllabus is found on.  Usually `response.url`.
- `source_anchor`: The label associated with the request to the syllabus.
  Sometimes, if the link to the syllabus is an `<a>` tag, it is sufficient to
  use the text of that tag as the `source_anchor`.  However, the `<a>` tag text
  is often something extremely generic (e.g., "Syllabus"), and so it may be more
  appropriate to set the `source_anchor` in those situations to something more
  descriptive if it is available (e.g., the course number).

Also note the `file_urls` value.  For some scrapers, it may be efficient to
implement the `extract_links` method to iterate over links to syllabi.  If
implemented, an `extract_links` method will `yield` tuples containing a URL and
an anchor.  Requests are made to these URLs, and the resulting `response`
objects are converted into WARC files as well.

If it's possible that there might be no links for `extract_links` to extract,
the `require_files` flag can optionally be set to `True` in the `meta` of the
request.  With this setting, no WARC files will be saved unless `extract_links`
`yield`s at least one tuple.  This can be useful for preventing the downloading
of unecessary files.  As an example, see
[`howard.py`](../osp_scraper/spiders/howard.py).

Here's an example of `extract_links` implemented in
[`inverhills.py`](../osp_scraper/spiders/inverhills.py):

```python
def extract_links(self, response):
	for a_tag in response.css(".pdf"):
	href = a_tag.css("::attr(href)").extract_first()
	title = a_tag.css("::attr(title)").extract_first()
	yield (href, title)
```

For more information, see the documentation in the
[`CustomSpider`](../osp_scraper/spiders/CustomSpider.py) class.
