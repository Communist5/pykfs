import sys
import os
import argparse
import pykfs
from pykfs.settings import get_script_settings
import logging


def email(value):
    from validate_email import validate_email
    if not validate_email(value):
        raise ValueError("'{0}' is an invalid email address".format(value))
    return value


def url(value):
    import re
    # Taken from django
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if not regex.match(value):
        raise ValueError("'{0}' is not a valid url")
    return value


SETTINGS_FILE_ARGS = [
    {
        "name": "settings_file",
        "option_strings": ["--settings-file"],
        "type": str,
        "action": "store",
        "metavar": "SETTINGS_FILE",
        "default": None,
        "help":
            "The settings file to use while running this script.  Defaults to `~/.pykfsrc`",
    },
]


class Script(object):
    """ Base for runnable commad line scripts """

    use_settings_file = True
    args = []
    conflicts = []
    log = logging

    @classmethod
    def get_script_name(cls):
        return cls.__name__.lower()

    @classmethod
    def execute(cls, settings=None):
        tokens = sys.argv[1:]
        script = cls()
        sys.exit(script.run(tokens, settings=settings))

    def get_data_archive(self):
        data_file_dir = os.path.join(os.path.dirname(pykfs.__file__), "data-files", "scripts")
        data_file_name = "{}.tar.gz".format(self.get_script_name())
        archive = os.path.join(data_file_dir, data_file_name)
        return archive

    def get_data_source(self):
        data_file_dir = os.path.join(
            os.getcwd(), "data", "scripts", self.get_script_name()
        )
        return data_file_dir


    def run(self, tokens, settings=None):
        try:
            self.tokens = tokens
            self._parse_args()
            self._load_settings(settings)
            self._determine_arg_values()
            self.do_script()
        except:
            self.on_failure()
            raise
        return 0

    def on_failure(self):
        pass

    def _load_settings(self, settings):
        self.settings = settings or {}
        if not self.settings and self.use_settings_file:
            self.settings = get_script_settings(self.get_script_name())
        for key in self.settings:
            if key not in [arg["name"] for arg in self.args]:
                self._print_warning("Unknown setting '{0}'.\n".format(key))


    def _print_warning(self, warning):
        sys.stderr.write("WARNING: {0}".format(warning));

    def error(self, message, parser_err=True, exitcode=1):
        if parser_err:
            self.parser.error(message)
        else:
            sys.stderr.write("ERROR: {0}\n\n".format(message))
            sys.exit(exitcode)

    def _parse_args(self):
        self.script_defaults = {}
        self.parser = argparse.ArgumentParser(description=type(self).__doc__.strip())
        for arg in self.args:
            self._add_arg(**arg)
        if self.use_settings_file:
            for arg in SETTINGS_FILE_ARGS:
                self._add_arg(**arg)
        self.options = self.parser.parse_args(self.tokens)

    def _add_arg(self, name, option_strings=[], default=None, **kwargs):
        kwargs["dest"] = name
        kwargs["default"] = None
        self.script_defaults[name] = default
        if callable(default):
            self.script_default[name] = default()
        self.parser.add_argument(*option_strings, **kwargs)

    def _determine_arg_values(self):
        for conflict in self.conflicts:
            self._check_conflicting(*conflict)
        for arg in self.args:
            argname = arg["name"]
            value = None
            if hasattr(self.options, argname):
                value = getattr(self.options, argname)
            if value is None:
                if argname in self.settings:
                    value = self.settings[argname]
                else:
                    value = self.script_defaults[argname]
            if hasattr(self, argname):
                raise KeyError("Conflicting variable name '{}' on script".format(argname))
            setattr(self, argname, value)

    def _check_conflicting(self, option1, option2):
        hasvalue1 = getattr(self.options, option1) != None
        hasvalue2 = getattr(self.options, option2) != None
        if hasvalue1:
            self._overwrite_setting(option2)
            if  hasvalue2:
                self.error(
                    "The '--{0}' option cannot be used with the '--{1}' "
                    "option".format(option1, option2)
                )
        if hasvalue2:
            self._overwrite_setting(option1)
        if option1 in self.settings and option2 in self.settings:
            self.error(
                "The '{0}' setting cannot be used with the '{1}' "
                "option".format(option1, option2)
            )

    def _overwrite_setting(self, setting):
            self.settings.pop(setting, None)

    def do_script(self):
        raise NotImplementedError()

    def get_error_code(self, e):
        return 1

    def stdout(self, value):
        sys.stdout.write(str(value))

    def stderr(self, value):
        sys.stderr.write(value)
