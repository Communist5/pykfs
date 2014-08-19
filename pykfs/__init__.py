import os.path


VERSION = (0, 2, 1, 0)


def get_version():
    return ".".join([str(x) for x in VERSION])


def get_data_dir():
    return os.path.join(os.path.dirname(__file__), "data")
