# Scrapy settings for osp_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

import os

from .. import templates

BOT_NAME = 'osp_scraper'

SPIDER_MODULES = ['osp_scraper.spiders', 'osp_site_scrapers']
NEWSPIDER_MODULE = 'osp_site_scrapers'

# NOTE: Add version number of 'osp-scraper'?
USER_AGENT = "OSPScraper (+https://www.opensyllabusproject.org)"

# Don't follow robots.txt.
ROBOTSTXT_OBEY = False

# Maximum file size to download.  This value is currently three times the
# largest known size of a syllabus in our collection.
DOWNLOAD_MAXSIZE = 30 * (1024 * 1024) # 30 MiB

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'osp_scraper.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'osp_scraper.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
}

# WARC Pipelines are added at the scraper level
ITEM_PIPELINES = {}

# Configure WarcFilesPipeline & WarcStorePipeline
FILES_STORE = None

# Downloader middleware to enforce allowed_domains & allowed_paths for files - this should come first
DOWNLOADER_MIDDLEWARES = {
    'osp_scraper.downloadermiddlewares.FilterMiddleware': 50,
}

SPIDER_MIDDLEWARES = {
    # disable builtin middlewares
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,

    "osp_scraper.spidermiddlewares.DepthMiddleware": 901,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Templates
TEMPLATES_DIR = templates.__path__._path[0]

# ENV

DOWNLOAD_DELAY = int(os.environ.get(
    'DOWNLOAD_DELAY', 3
))

LOG_LEVEL = os.environ.get(
    'LOG_LEVEL', 'WARNING'
)

FILES_STORE = os.environ.get(
    'FILES_STORE', 's3://syllascrape/test/'
)
