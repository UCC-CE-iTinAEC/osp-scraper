import subprocess
import os.path

# helper func to get revision from a development checkout
def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])

fname = os.path.join(os.path.dirname(__file__), 'git_revision')
if os.path.exists(fname):
    with open(fname) as f:
        git_revision = f.readline().strip()
else:
    git_revision = get_git_revision_short_hash().decode('utf-8').strip()
