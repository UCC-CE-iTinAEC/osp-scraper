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

def file_path(url, retrieved, default_ext=''):
    """return a path for a downloaded file. Files will be named `<ext>/<url_hash>-<epoch>.<ext>`

    @arg str url: the original URL
    @arg int retrieved: timestamp URL was retrieved
    @arg str default_ext: default extension to use if URL doesn't have one
    @rtype: str
    """
    url_hash = hashlib.md5(to_bytes(url)).hexdigest()
    ext = os.path.splitext(urlparse(url).path)[1].lower() or ".%s" % default_ext
    return '{:s}/{:s}-{:d}{:s}'.format(ext[1:], url_hash, retrieved, ext)

def guess_extension(mimetype):
    """guess a file extension from mimetype, without leading `.`

    Returns `unknown` if an extension could not be guessed
    """
    x = (mimetypes.guess_extension(mimetype.split(';')[0]) or '.unknown')[1:]
    return x if x != 'htm' else 'html'