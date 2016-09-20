# Syllascrape

Syllascrape is a [Scrapy](http://scrapy.org) spider for the [Open Syllabus Project](http://opensyllabusproject.org/).

Please see [Scrapy's docs](http://doc.scrapy.org) for instructions on how to
install & use Scrapy; this README only highlights customizations for Syllascrape

## Settings

`FILES_STORE` is the root path to save files. This may be a path on the local
filesystem, or an S3 URL like `s3://<bucket>/<prefix>/`. If using S3, the
bucket must already exist. You must include the trailing slash when using S3.

## Output

Output files will be stored in the location specified by the `FILES_STORE`
setting. Files will be named as `<ext>/<url_hash>-<epoch>.<ext>`, with a
corresponding `.json` file containing metadata (described below).

Due to the use of timestamps, the dataset is immutable, and provides a
consistent view of the data at past points in time. To obtain the most recent
items:

1. reverse sort the files by name
2. group by `url_hash`
3. take the first item from each group.

See `syllascrape.storage.newest_files` for a helper function that implements
this algorithm.

### Metadata

The following metadata is saved for each downloaded file; all fields will be
present, with missing values represented by the empty string.

* url: url of the file
* domain: hostname & port
* source_url: url that linked to the file
* source_anchor: anchor text on source page
* retrieved: integer seconds since epoch
* spider_name: spider name
* spider_revision: git revision number for syllascrape code
* spider_parameters: dict of spider parameters (starting urls, allowed domains, etc.)
* spider_run_id: unique identifier for spider run
* checksum: MD5 of content
* length: length of content
* mimetype: Content-Type header from response
* depth: the crawl depth at that

## Spiders
All spiders should inherit from `syllascrape.spiders.Spider`.

`start_urls` is a list of initial URLs to begin the crawl.

`allowed_file_types` is a set of binary filename extensions that should be
downloaded (*without* leading `.`). All text files (HTML, XML, etc.) will be
automatically saved. Defaults to `pdf, doc, docx`.

`filters` a list of syllascrape.filterware.Filter`s that control the scope of
`the crawl. See its documentation for details.

## Legacy Format

A script to convert to the legacy data format is in
`bin/write_legacy_logs.py`. Note that data files will be hard linked to save
space.

## Celery

Syllascrape supports running spiders under
[Celery](http://www.celeryproject.org/). Celery looks for a module
`celeryconfig.py` somewhere on the PYTHONPATH. To start the celery worker,
from the project directory run:

    $ celery -A syllascrape worker -l info

Also installed is [Flower](https://flower.readthedocs.io/en/latest/) a nice
web UI for [monitoring celery](http://localhost:5555/). Run it as:

    $ flower -A syllascrape

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
