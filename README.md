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
