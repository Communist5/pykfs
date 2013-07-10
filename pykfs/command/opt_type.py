NO_PARAMS = 0
ONE_PARAM = 1
N_PARAMS = 2


class _FlagType(object):

    default = False

    def is_valid(self, value):
        return value == True or value == False

    def error_string(self, value):
        return "must be either True or False"

    def set_value(self, command, attribute, params):
        setattr(command, attribute, True)
        return params


class _IntType(object):

    default = 0

    def is_valid(self, value):
        return isinstance(value, int)

    def error_string(self, value):
        return "must be an integer"

    def set_value(self, command, attribute, params):
        setattr(command, attribute, int(params[0]))
        return params[1:]


class _StringType(object):

    default = ""

    def is_valid(self, value):
        return isinstance(value, str)

    def error_string(self, value):
        return "must be an string"

    def set_value(self, command, attribute, params):
        setattr(command, attribute, params[0])
        return params[1:]


class _MultipleStringType(object):

    default = []

    def is_valid(self, value):
        return isinstance(value, list) and \
               all([isinstance(x, str) for x in value])

    def error_string(self, value):
        return "must be a list of strings"

    def set_value(self, command, attribute, params):
        setattr(command, attribute, params[:])
        return []


FLAG = _FlagType()
INT = _IntType()
STRING = _StringType()
STRING_LIST = _MultipleStringType()
