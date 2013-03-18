from pykfs.githooks.hookobj import PostReceive
import logging


def post_receive(settings={}):
    hook = PostReceive(settings=settings)
    return hook()


