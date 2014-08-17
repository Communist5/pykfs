import sh
import os
import re
git = sh.git


def setgitdir(func):
    def f(*args, **kwargs):
        if 'gitdir' not in kwargs or kwargs['gitdir'] == None:
            kwargs['gitdir'] = "{}/.git".format(os.getcwd())
        return func(*args, **kwargs)
    return f


def setdir(func):
    def f(*args, **kwargs):
        directory = kwargs.pop('directory', None)
        if directory:
            cwd = os.getcwd()
            os.chdir(directory)
            try:
                return func(*args, **kwargs)
            finally:
                os.chdir(cwd)
        else:
            return func(*args, **kwargs)
    return f


@setgitdir
def commit_message(sha, gitdir, short=False):
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
def gettags(sha, gitdir):
    rval = git('--git-dir', gitdir, 'tag', contains=sha)
    tags = rval.split()
    return tags


@setdir
def init(*args):
    rval = git.init(*args)
    return rval


@setdir
def addall(*args):
    rval = git.add("-A", *args)
    return rval


@setdir
def commit(message):
    rval = git.commit("-m", message)
    return rval


@setdir
def setorigin(url, fetch=False):
    rval = git.remote.add("origin", url)
    if fetch:
        rval = str(rval) + str(git.fetch("origin"))
    return rval

@setdir
def setupstream(branch, upstream):
    rval = git.branch(branch, "--set-upstream-to", upstream)
    return rval


def isversion(tag):
    return bool(re.match("v[^a-z]", tag, flags=re.I))
