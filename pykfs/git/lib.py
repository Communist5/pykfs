import sh
import os
git = sh.git


def commit_message(sha, cwd=None, short=False):
    if not cwd:
        cwd = os.getcwd()
    rval = git('cat-file', 'commit', sha, _cwd=cwd)
    lines = rval.split('\n')
    index = 0
    while index < len(lines):
        if not lines[index]:
            break
        index += 1
    if short:
        return lines[index + 1]
    return "\n".join(lines[index + 1:-1])


def gettag(sha, cwd=None):
    pass
