import os.path
import logging


logging.getLogger(__name__).addHandler(logging.NullHandler())


VERSION = (0, 2, 2, 1)


def get_version():
    return ".".join([str(x) for x in VERSION])


def get_data_dir():
    return os.path.join(os.path.dirname(__file__), "data")
