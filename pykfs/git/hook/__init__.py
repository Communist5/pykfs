from pykfs.git.hook.hookobj import PostReceive, CommitMsg, PreReceive


def pre_receive(settings={}):
    hook = PreReceive(settings=settings)
    return hook()


def post_receive(settings={}):
    hook = PostReceive(settings=settings)
    return hook()


def commit_msg(settings={}):
    hook = CommitMsg(settings=settings)
    return hook()
