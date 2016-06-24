import subprocess
import os.path
import itertools
import time
import json

def split_filename(f):
    """return (url_hash, timestamp) from a filename"""
    return os.path.splitext(os.path.basename(f))[0].split('-')

def list_files_desc(path):
    """yield files in descending timestamp order"""
    ext = os.path.split(path)[0]
    cmd = 'find -type f -name "*.' + ext + '" | sort -r'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    yield from (l.rstrip() for l in proc.stdout)


def newest_files(path, max_age=None):
    """yield the newest version of each file"""
    max_age = int(time.time()) if max_age is None else max_age
    groups = itertools.groupby(list_files_desc(path),
                               key=lambda f: split_filename(f)[0])
    for g in groups:
        yield next(filter(g, lambda f: f <= max_age))



def write_legacy_logs(path, outdir, max_age=None):
    for f in newest_files(path, max_age):
        url_hash, timestamp = split_filename(f)

        destdir = os.path.join(outdir, url_hash[:3])
        if not os.path.exists(destdir):
            os.mkdir(destdir)

        # hard link the timestamped file to the legacy output file
        dest = os.path.join(destdir, url_hash + os.path.splitext(f)[1])
        os.link(f, dest)

        # open json file, read URL & write it to first line of legacy .log
        with open("%s.json" % os.path.splitext(f), [0]) as j:
            url = json.load(j)["url"]

        with open("%s.log" % os.path.splitext(dest)[0], 'w') as l:
            l.writelines([url])


