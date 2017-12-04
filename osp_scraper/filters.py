import logging
import os.path
import re
import urllib.parse

from osp_scraper.filterware import Filter

logger = logging.getLogger(__name__)

# a list of base domains to blacklist; subdomains blocked too
blacklist_domains = [
    'facebook.com',
    'reddit.com',
    'twitter.com',
    'linkedin.com',
    'wikipedia.org',
]

# Common file extensions that are not followed if they occur in links
# modified list from:
# https://github.com/scrapy/scrapy/blob/dcb279bd6cc85cf1743b548e44b050edba6a2ed8/scrapy/linkextractors/__init__.py
blacklist_extensions = [
    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',

    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a',

    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'ods', 'odg', 'odp',

    # other
    'css', 'exe', 'bin', 'rss', 'zip', 'rar',
]


def make_filters(seed_urls, max_hops_from_seed):
    """Generate filters for a spider from a list of URLs.

    * Allow paths with matching prefix to infinite depth
    * Allow same hostname to max depth of 2
    * Allow other domains to max depth of 1

    Args:
        seed_urls (list)
    """
    if not seed_urls:
        raise ValueError("List of URLs must be non-empty")

    filters = []

    domain_blacklist_re = r"(^.*\.)?({})$".format(
        "|".join(map(re.escape, blacklist_domains))
    )

    # blacklist domains
    filters.append(
        Filter.compile(
            'deny',
            pattern='regex',
            hostname=domain_blacklist_re
        )
    )

    extension_blacklist_re = r"^.*\.({})$".format(
        "|".join(blacklist_extensions)
    )

    # blacklist extentions
    filters.append(
        Filter.compile(
            'deny',
            pattern='regex',
            path=extension_blacklist_re
        )
    )

    filters.append(
        Filter.compile(
            'deny',
            max_hops_from_seed=max_hops_from_seed,
            invert=True
        )
    )

    # merge parameters from several seed urls, with unique domains & paths
    prefixes = set()
    hostnames = set()

    for url in seed_urls:
        u = urllib.parse.urlparse(url)
        if not u.hostname:
            msg = "Input '{0}' does not have a hostname.  Remove or fix this URL."
            logger.warning(msg.format(url))
            continue

        prefix = re.escape((os.path.dirname(u.path) + "/").replace("//", "/"))
        hostname = re.escape(u.hostname)
        port = re.escape(str(u.port)) if u.port else None

        prefixes.add((hostname, port, prefix))
        hostnames.add((hostname, port))

    for hostname, port, prefix in prefixes:
        # allow prefix to infinite depth
        filters.append(
            Filter.compile(
                'allow',
                pattern='regex',
                hostname=hostname,
                port=port,
                path=prefix + ".*"
            )
        )

    for hostname, port in hostnames:
        # allow same hostname to max depth 2
        filters.append(
            Filter.compile(
                'allow',
                pattern='regex',
                hostname=hostname,
                port=port,
                max_depth=2
            )
        )

    # allow other domains w/ max depth 1
    filters.append(Filter.compile('allow', max_depth=1))

    return filters
