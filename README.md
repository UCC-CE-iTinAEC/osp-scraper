# Syllascrape

Syllascrape is a [Scrapy](http://scrapy.org) spider for the [Open Syllabus Project](http://opensyllabusproject.org/).

Please see [Scrapy's docs](http://doc.scrapy.org) for instructions on how to
install & use Scrapy; this README only highlights customizations for Syllascrape

## Settings

`FILES_STORE` is the root path to save files. This may be a path on the local
filesystem, or an S3 URL like `s3://<bucket>/<prefix>/`. If using S3, the
bucket must already exist. You must include the trailing slash when using S3.

`FILES_EXTENSTIONS` is a set of binary filename extensions that should be
downloaded (*without* leading `.`). All text files (HTML, XML, etc.) will be
automatically saved.

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

### Metadata The following metadata is saved for each downloaded file; all
fields will be present, with missing values represented by the empty string.

* url: url of the file
* domain: hostname & port
* source_url: url that linked to the file
* source_anchor: anchor text on source page
* retrieved: integer seconds since epoch
* spider_name: spider name
* spider_revision: git revision number for syllascrape code
* spider_parameters: dict of spider parameters (starting urls, allowed domains, etc.)
* checksum: MD5 of content
* length: length of content
* mimetype: Content-Type header from response


## Spiders
All spiders should inherit from `syllascrape.spiders.Spider`.

The `allowed_domains` attribute is a list of domains the spider may crawl;
note that this includes subdomains as well. If omitted, any domain may be
crawled.

The `allowed_paths` attribute is a list of path prefixes the spider may
crawl. If omitted, any path may be crawled.

`start_urls` are a list of URLs to begin crawling at.

All spiders must have a string `name` (must be a valid Python identifier).

Spiders provide several methods that can be overridden to customize which
links are crawled; see the source for details.

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
web UI for monitoring celery. Run it as:

    $ flower -A syllascrape

By default, it listens on http://localhost:5555/ .

## Crawling from CSV

The `bin/csv_prefix_crawler.py` takes a CSV file with a
seed URL on each line, and fires of Celery crawl tasks. If the path component
ends with a `/` it will be used-as is; otherwise the final path component is
assumed to be a filename and will be dropped.
