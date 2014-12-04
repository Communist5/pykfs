import sh
import os
import re
import logging


LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())


def git(*args, **kwargs):
    command = sh.git.bake(*args, **kwargs)
    LOG.info("Executing '{0}'".format(command))
    rval = ""
    for line in command(_iter = True):
        LOG.info(">>> {0}".format(line[:-1]))
        rval += line
    return rval


def resolve_git_dir(start=None):
    value = None
    branch, leaf = os.path.split(start)
    if leaf == ".git"  or os.path.basename(branch) == ".git":
        value = start
    else:
        directory = start or os.getcwd()
        while not os.path.exists() and directory and directory != '/':
            gitdir = os.path.join(directory, ".git")
            if os.isdir(gitdir):
                value = gitdir
    if value:
        LOG.debug("Git directory for '{0}' resolved to '{1}'".format(start, value))
    else:
        LOG.warning("Unable to find git directory for '{0}'".format(start))
    return value


def setgitdir(func):
    def f(*args, **kwargs):
        if 'gitdir' not in kwargs or kwargs['gitdir'] == None:
            kwargs['gitdir'] = os.getcwd()
        kwargs['gitdir'] = resolve_git_dir(kwargs['gitdir'])
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
    rval = git("init", *args)
    return rval


@setdir
def addall(*args):
    rval = git("add", "-A", *args)
    return rval


@setdir
def commit(message):
    rval = git("commit", "-m", "\"{0}\"".format(message))
    return rval


@setdir
def setorigin(url, fetch=False):
    rval = git("remote", "add", "origin", url)
    if fetch:
        rval = str(rval) + str(git("fetch", "origin"))
    return rval

@setdir
def setupstream(branch, upstream):
    rval = git("branch", branch, "--set-upstream-to", upstream)
    return rval


def isversion(tag):
    return bool(re.match("v[^a-z]", tag, flags=re.I))
