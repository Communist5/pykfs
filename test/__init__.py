import logging


LOGGING_CONFIG = {
    "format": '- %(asctime)s - %(levelname)s - %(message)s',
    "level": logging.DEBUG,
    "datefmt": '%Y-%m-%d %H:%M:%S',
}


def setup_package():
    logging.basicConfig(**LOGGING_CONFIG)
