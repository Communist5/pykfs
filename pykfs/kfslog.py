import logging
import logging.config
import datetime as dt
from pykfs.bashcolor import bashcolor


class KFSFormatter(logging.Formatter):
    default_format = "{timeplus} > {nameplus} > {levelplus} {message}"
    default_datefmt = "%Y-%m-%dT%H:%M:%S:%f"
    levelcolors = {
        "DEBUG": "BOLD",
        "INFO": "CYAN_BOLD",
        "WARNING": "YELLOW_BOLD",
        "ERROR": "RED_BOLD",
        "CRITICAL": "BIG_ERROR",
    }

    def __init__(self, fmt=None, datefmt=None, color=False):
        fmt = fmt or self.default_format
        datefmt = datefmt or self.default_datefmt
        self.color = color
        super(KFSFormatter, self).__init__(fmt, datefmt)

    def format(self, record):
        asctime = self.formatTime(record)
        line = self._fmt.format(
            timeplus=self.gettimeplus(record),
            nameplus=self.getnameplus(record),
            levelplus=self.getlevelplus(record),
            asctime=asctime,
            message=record.msg,
            **record.__dict__
        )
        if record.exc_info:
            line += "\n{0}".format(self.formatException(record.exc_info))
        return line

    def formatException(self, exc_info):
        value = super(KFSFormatter, self).formatException(exc_info)
        value = value.replace("\n", "\n>>> ")
        value = ">>> {}".format(value)
        if self.color:
            value = bashcolor(value, "RED")
        return value

    def getdateplus(self, record):
        date = self.formatDate(record, "%y-%m-%d")
        date = self.color and bashcolor(date, "GREEN_BOLD") or date
        time = self.formatTime(record, "%H:%M:%S")
        time = self.color and bashcolor(time, "GREEN_BOLD") or time
        micro = self.formatTime(record, "%f")
        return "{0} | {1} | {2}".format(date, time, micro)

    def gettimeplus(self, record):
        time = self.formatTime(record, "%H:%M:%S")
        micro = self.formatTime(record, "%f")
        time = self.color and bashcolor(time, "GREEN_BOLD") or time
        return "{0} :: {1}".format(time, micro)

    def getnameplus(self, record):
        return self.color and bashcolor(record.name, "PURPLE_BOLD") or record.name

    def getlevelplus(self, record):
        levelplus = "{:>10}".format("[{}]".format(record.levelname))
        color = self.levelcolors[record.levelname]
        return self.color and bashcolor(levelplus, color) or levelplus

    def formatTime(self, record, datefmt=None):
        datefmt = datefmt or self.datefmt
        recorded = dt.datetime.fromtimestamp(record.created)
        return recorded.strftime(datefmt)


CONSOLE_HANDLER = {
    "class": "logging.StreamHandler",
    "formatter": "console",
}

CONSOLE_FORMATTER = {
    "()": "pykfs.kfslog.KFSFormatter",
    "fmt": "> {timeplus} > {nameplus} > {levelplus} {message}",
    "color": True,
}

ROOT_HANDLER = {
    "class": "logging.StreamHandler",
    "formatter": "root",
}

ROOT_FORMATTER = {
    "()": "pykfs.kfslog.KFSFormatter",
    "fmt": "> {timeplus} > {levelplus} {message}",
    "color": True,
}

FILE_FORMATTER = {
    "()": "pykfs.kfslog.KFSFormatter",
    "fmt": "> {asctimeplus} > {nameplus} > {levelplus} {message}",
    "color": False,
}

DEFAULT_HANDLERS = {
    "console": CONSOLE_HANDLER,
    "root": ROOT_HANDLER,
}

DEFAULT_FORMATTERS = {
    "console": CONSOLE_FORMATTER,
    "file": FILE_FORMATTER,
    "root": ROOT_FORMATTER,
}

DEFAULT_LOGGER_CONFIG = {
    "level": "INFO",
    "handlers": ["console"],
}


def quick_log_config(loggers=None, handlers=DEFAULT_HANDLERS, formatters=DEFAULT_FORMATTERS,
                     level="INFO"):
    configdict = {
        "version": 1,
        "handlers": handlers,
        "formatters": formatters,
    }
    if loggers:
        loggers = _get_loggers_config(loggers, level)
        configdict["loggers"] = loggers
    else:
        configdict["root"] = _get_default_root_config(level)
    logging.config.dictConfig(configdict)
    return configdict


def _get_loggers_config(loggers, level):
    if isinstance(loggers, dict):
        return
    return dict([(logger, _get_default_loggers_config(level)) for logger in loggers])


def _get_default_loggers_config(level):
    return {
        "level": level,
        "handlers": ["console"],
    }


def _get_default_root_config(level):
    return {
        "level": level,
        "handlers": ["root"],
    }

