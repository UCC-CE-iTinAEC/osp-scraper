from urllib.parse import urlparse
from scrapy.utils.python import to_bytes
import os.path
import hashlib
import logging
import mimetypes

def extract_domain(url):
    """return the domain, with implied port"""
    u = urlparse(url)
    if not u.netloc or ':' in u.netloc:
        return u.netloc
    else:
        return "%s%s" % (u.netloc,
                         ':80' if u.scheme == 'http' else ':443' if u.scheme == 'https' else '' )

def guess_extension(mimetype):
    """guess a file extension from mimetype, without leading `.`

    Returns `unknown` if an extension could not be guessed
    """
    x = (mimetypes.guess_extension(mimetype.split(';')[0]) or '.unknown')[1:]
    return x if x != 'htm' else 'html'