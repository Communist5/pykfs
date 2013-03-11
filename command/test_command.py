#!/usr/bin/python2.7
import pykfs.command as command
import sys
from pykfs.command import opt_type
from pykfs.command.exception import InvalidOptionException
from option import Option
import unittest
from mock import patch


class FooBar(command.Command):
    options = [Option("INT", "This int option will print out when used",
                      short="-i", otype=opt_type.INT),
               Option("MANDATORY_INT", "This int option will print out when "
                      "used", short="-m", mandatory=True, otype=opt_type.INT),
               Option("MANDATORY_POSITIONAL_INT", "This int option will print "
                      "out when used", short="-n", position=1, mandatory=True,
                      otype=opt_type.INT),
               Option("POSITIONAL_STRING", "This string option will print out "
                      "when used, and print nothing if not used", short="-s",
                      position=True, otype=opt_type.STRING),
              ]

    def run(self):
        self.wasrun = True
        for option in self.options:
            print "Value of '{}' is '{}'".format(option.name, getattr(self, option.lower))

    def describe(self):
        return "A test command"


class NoOptions(command.Command):
    options = []

    def run(self):
        self.wasrun = True

    def describe(self):
        return "A command with no options"


class TestCommand(unittest.TestCase):

    def testMandatory(self):
        foobar = FooBar()
        try:
            foobar()
            self.fail()
        except InvalidOptionException as e:
            self.assertTrue('--mandatory-int' in e.message)
            self.assertTrue('--mandatory-positional-int' in e.message)

    def testNotMandatory(self):
        foobar = FooBar()
        foobar("-m", "1", "-n", "2")
        self.assertTrue(foobar.wasrun)
        self.assertEqual(foobar.mandatory_int, 1)
        self.assertEqual(foobar.mandatory_positional_int, 2)

    def testInvalidOptionNoPostions(self):
        no_op = NoOptions()
        self.assertRaisesRegexp(InvalidOptionException, "foo", no_op, "foo")

    def testHelpWithOption(self):
        no_op = NoOptions()
        with patch.object(no_op, "get_help") as mock_help:
            no_op("-h")
            self.assertTrue(mock_help.called)


if __name__ == "__main__":
    command = FooBar(called_command=sys.argv[0])
    command(*sys.argv[1:])

