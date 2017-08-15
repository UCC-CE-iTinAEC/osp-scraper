

import attr

from collections import defaultdict
from urllib.parse import urlparse


@attr.s
class SeedURLList:

    urls = attr.ib()

    @classmethod
    def from_file(cls, path):
        """Hydrate from a file of URLs, one URL per line.

        Args:
            path (str)

        Returns cls
        """
        with open(path) as fh:
            return cls(fh.read().splitlines())

    def group_by_domain(self):
        """Yield groups of URLs with the same domain.

        Returns: dict of {domain -> URL list}
        """
        groups = defaultdict(list)

        for url in self.urls:
            domain = urlparse(url).netloc
            groups[domain].append(url)

        return groups
