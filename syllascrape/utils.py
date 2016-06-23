from urllib.parse import urlparse

def extract_domain(url):
    """return the domain, with implied port"""
    u = urlparse(url)
    if not u.netloc or ':' in u.netloc:
        return u.netloc
    else:
        return "%s%s" % (u.netloc,
                         ':80' if u.scheme == 'http' else ':443' if u.scheme == 'https' else '' )