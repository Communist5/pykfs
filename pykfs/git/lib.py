import sh
import os
import re
git = sh.git


def setgitdir(func):
    def f(*args, **kwargs):
        if 'gitdir' in kwargs and kwargs['gitdir'] == None:
            kwargs['gitdir'] = os.getcwd
        return func(*args, **kwargs)
    return f


@setgitdir
def commit_message(sha, gitdir=None, short=False):
    rval = git('--git-dir', gitdir, 'cat-file', 'commit', sha)
    lines = rval.split('\n')
    index = 0
    while index < len(lines):
        if not lines[index]:
            break
        index += 1
    if short:
        return lines[index + 1]
    return "\n".join(lines[index + 1:-1])


@setgitdir
def gettags(sha, gitdir=None):
    rval = git('--git-dir', gitdir, 'tag', contains=sha)
    tags = rval.split()
    return tags


def isversion(tag):
    return bool(re.match("v[^a-z]", tag, flags=re.I))
