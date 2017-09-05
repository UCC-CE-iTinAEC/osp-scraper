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


def make_filters(seed_urls):
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

    blacklist_re = r"(^.*\.)?({})$".format(
        "|".join(map(re.escape, blacklist_domains))
    )

    # blacklist domains
    filters.append(
        Filter.compile(
            'deny',
            pattern='regex',
            hostname=blacklist_re
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

    # TODO: Read max depths from settings?

    for hostname, port, prefix in prefixes:
        # allow same prefix to max depth 100.
        filters.append(
            Filter.compile(
                'allow',
                pattern='regex',
                hostname=hostname,
                port=port,
                path=prefix + ".*",
                max_hops_from_seed=2000
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
