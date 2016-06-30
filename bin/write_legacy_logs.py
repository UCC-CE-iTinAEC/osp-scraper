#!/usr/bin/env python3

import sys
import syllascrape.storage
import os.path

def usage():
    print("%s <download_dir> <output_dir>" % os.path.basename(sys.argv[0]))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
    else:
        syllascrape.storage.write_legacy_logs(sys.argv[1], sys.argv[2])