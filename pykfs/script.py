import sys
import argparse
from pykfs.settings import get_script_settings


class Script(object):
    """ Base for runnable commad line scripts """

    name = ""
    args = []
    conflicts = []

    @classmethod
    def execute(cls, settings=None):
        tokens = sys.argv[1:]
        script = cls()
        sys.exit(script.run(tokens, settings=settings))

    def run(self, tokens, settings=None):
        self._load_settings(settings)
        self.tokens = tokens
        self._parse_args()
        self.do_script()
        return 0

    def _load_settings(self, settings):
        self.settings = settings or {}
        if not settings:
            self.settings = get_script_settings(self.name)
        for x in self.settings:
            if x not in [arg["name"] for arg in self.args]:
                self._print_warning("Unknown setting '{0}'.\n".format(x))

    def _print_warning(self, warning):
        sys.stderr.write("WARNING: {0}".format(warning));

    def error(self, message, parser_err=True):
        if parser_err:
            self.parser.error(message)
        else:
            sys.stderr.write("ERROR: {0}\n\n".format(message))
            sys.exit(1)

    def _parse_args(self):
        self.script_defaults = {}
        self.parser = argparse.ArgumentParser(description=type(self).__doc__.strip())
        for arg in self.args:
            self._add_arg(**arg)
        self.options = self.parser.parse_args(self.tokens)
        self._determine_arg_values()

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
