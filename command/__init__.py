from pykfs.command import option
from pykfs.command.exception import InvalidOptionException
import sys
from StringIO import StringIO


class Command(object):
    _default_options = [option.HelpOption()]
    example = None

    def __init__(self, called_command=None):
        self._optmap = {}
        self._positions = []
        self._mandatory = set([])
        self._options_used = set([])
        self.called_command = called_command
        self.options.extend(self._default_options)

    def __call__(self, *args):
        if self.called_command:
            try:
                self._call(*args)
            except InvalidOptionException as e:
                sys.stderr.write("Command Failed: {}\n".format(e.message))
                print self.get_help()
        else:
            return self._call(*args)

    def call(self, *args):
        return self(*args)

    def get_help(self):
        helpstr = StringIO()
        position_str = " ".join(["[{}]".format(o.name) for o in self._positions])
        helpstr.write("Usage: {} {} [OPTION]...\n".format(self.name, position_str))
        helpstr.write("{}\n".format(self.describe()))
        if self.example:
            helpstr.write("{}\n".format(self.example))
        helpstr.write("\nOptions:\n")
        maxflag = max([len(option.flag) for option in self.options])
        for option in self.options:
            helpstr.write("  {:2} {:<{maxflag}} {}\n".format(option.short, option.flag, option.description,
                          maxflag=maxflag))
        return helpstr.getvalue()

    def run(self):
        raise NotImplementedError()

    def describe(self):
        raise NotImplementedError()

    def config_env(self):
        raise NotImplementedError()

    def _call(self, *args):
        self._compile_options()
        self._process_arguments(args)
        if not self._mandatory.issubset(self._options_used):
            error = "The following mandatory options are missing:\n"
            for option in self._mandatory - self._options_used:
                error += "    {}\n".format(option.flag)
            raise InvalidOptionException(error)
        if self.help:
            print self.get_help()
            return
        return self.run()

    def _compile_options(self):
        for option in self.options:
            self._optmap[option.short] = option
            self._optmap[option.flag] = option
            setattr(self, option.lower, option.default)
            self._set_position(option)
            if option.mandatory:
                self._mandatory.add(option)

    def _process_arguments(self, args):
        arglist = [arg for arg in args]
        self._positions_left = self._positions[:]
        return self._process_arguments_recursive(arglist)

    def _process_arguments_recursive(self, arglist):
        if not arglist:
            return
        option = None
        arg = arglist[0]
        if arg in self._optmap:
            option = self._optmap[arg]
            arglist.pop(0)
        else:
            try:
                option = self._positions_left.pop(0)
            except IndexError:
                _raise_unknown_option(arg)
        self._options_used.add(option)
        arglist = option(self, arglist)
        self._process_arguments_recursive(arglist)

    def _set_position(self, option):
        if None == option.position:
            return
        if isinstance(option.position, int):
            while len(self._positions) <= option.position:
                self._positions.append("_")
            self._positions[option.position] = option
        else:
            try:
                self._positions[self._positions.index("_")] = option
            except ValueError:
                self._positions.append(option)


def _raise_unknown_option(option):
    raise InvalidOptionException("Unknown option '{}'".format(option))


def call_bash(command_class):
    instance = command_class(called_command=sys.argv[0])
    instance(*sys.argv[1:])
