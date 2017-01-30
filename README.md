# OSP Scraper

OSP Scraper is a [Scrapy](http://scrapy.org) spider for the [Open Syllabus Project](http://opensyllabusproject.org/).

Please see [Scrapy's docs](http://doc.scrapy.org) for instructions on how to
install & use Scrapy; this README only highlights customizations for OSP Scraper

## Installation
Create a Python 3 environment
```
python3 -m venv env
```
Activate the environment (This needs to be done every time you open a new terminal)
```
. env/bin/activate
```
Install dependencies
```
pip install -r requirements.txt
```
Install OSP Scraper as a package for development
```
python setup.py develop
```

## Settings

`FILES_STORE` is the root path to save files. This may be a path on the local
filesystem, or an S3 URL like `s3://<bucket>/<prefix>/`. If using S3, the
bucket must already exist. You must include the trailing slash when using S3.

To set `FILES_STORE` to save files locally on your system, create a `.env` file in the root of the project with contents such as:
```
FILES_STORE="file://downloads/"
```

## Output

Output files will be stored as WARC files in the location specified by the
`FILES_STORE` setting. Files will be named as
`<spider_run_id>/<warc_id>.warc`. When in doubt, we aim for compatibility
with Common Crawl.

### WARC Records
We write 3 kinds of WARC records:

* for each spider run, a `warcinfo` record including the filters as JSON
* for each page, a `response` record with the bytes of the HTTP response (including reconstructed headers)
* for each page, a `metadata` record with info about the crawler (number of hops, etc)

### Variations from WARC standard
* we don't write `request` records.
* some header/field names have strange capitalization
* some fields are missing, including `WARC-IP-Address`

### Helpful links

* [WARC File Format](http://archive-access.sourceforge.net/warc/warc_file_format-0.16.html)
* [Some best practices](http://www.netpreserve.org/sites/default/files/resources/WARC_Guidelines_v1.pdf)
* [Common Crawl docs](http://commoncrawl.org/the-data/get-started/)
* [Common Crawl example](https://gist.github.com/Smerity/e750f0ef0ab9aa366558#file-bbc-warc)
* [Helpful slides](http://connect.ala.org/files/2015-06-27_ALCTS_PARS_PMIG_web_archives.pdf)
* [More WARC example files](https://mementoweb.github.io/SiteStory/warcfile_example.html)
* [Common Crawl Index](http://commoncrawl.org/2015/04/announcing-the-common-crawl-index/)

### A note on libraries

All of the Python WARC libraries are pretty terrible, `internetarchive/warc`
(and its various forks) seemed the least bad.

## Spiders
All spiders should inherit from `syllascrape.spiders.BaseSpider`.

`start_urls` is a list of initial URLs to begin the crawl.

`allowed_file_types` is a set of binary filename extensions that should be
downloaded (*without* leading `.`). All text files (HTML, XML, etc.) will be
automatically saved. Defaults to `pdf, doc, docx`.

`filters` a list of osp_scraper.filterware.Filter`s that control the scope of
`the crawl. See its documentation for details.

## Celery

OSP Scraper supports running spiders under
[Celery](http://www.celeryproject.org/). Celery looks for a module
`celeryconfig.py` somewhere on the PYTHONPATH. To start the celery worker,
from the project directory run:

    $ celery -A osp_scraper worker -l info

Also installed is [Flower](https://flower.readthedocs.io/en/latest/) a nice
web UI for [monitoring celery](http://localhost:5555/). Run it as:

    $ flower -A osp_scraper

### Celery/Scrapy Integration
Celery workers run as a daemon process & read tasks off a Redis queue.

Each task fires off a subprocess running scrapy/twisted.

When the subprocess exits, the task is finished.

Celery then starts a new daemon process for the next incoming task. This is
unusual - typically a daemon process handles 1000s of short tasks before
respawning), but seems to be needed to run twisted.

## Crawling from CSV

The `bin/csv_prefix_crawler.py` takes a CSV file with a
seed URL on each line, and fires of Celery crawl tasks. If the path component
ends with a `/` it will be used-as is; otherwise the final path component is
assumed to be a filename and will be dropped.

The `edu_repo_crawler.py` works with the Google spreadsheet: "USA EDU Repo"
