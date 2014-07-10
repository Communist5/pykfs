from unittest2 import TestCase
from pykfs import script
import logging


LOG = logging.getLogger(__name__)


class ErrorEncountered(Exception):
    pass

class SampleScript(script.Script):
    """ A sample script for testing """
    args = [
        {
            "name": "arg1", "option_strings": ['-a', '-arg1'], "const": True,
            "action": "store_const", "default": "foobar"
        },
        {
            "name": "arg2", "option_strings": ['-b', '-arg2'], "const": True,
            "action": "store_const", "default": None
        },
        {
            "name": "arg3", "option_strings": ['-c', '-arg3'], "action": "store",
            "default": "barbar"
        }
    ]
    conflicts = [
        ("arg1", "arg2")
    ]

    def __init__(self, results, *args, **kwargs):
        self.results = results
        super(SampleScript, self).__init__(*args, **kwargs)

    def error(self, *args, **kwargs):
        raise ErrorEncountered()

    def do_script(self):
        self.results["arg1"] = self.arg1
        self.results["arg2"] = self.arg2
        self.results["arg3"] = self.arg3


class TestScript(TestCase):

    def setUp(self):
        self.results = {}

    def test_run_command(self):
        command = SampleScript(self.results)
        command.run([])
        self.assertTrue(self.results)
        self.assertEqual("foobar", self.results["arg1"])
        self.assertEqual(None, self.results["arg2"])
        self.assertEqual("barbar", self.results["arg3"])

    def test_arg_parsed(self):
        command = SampleScript(self.results)
        command.run(["-a", "-c", "hello"])
        self.assertTrue(self.results)
        self.assertEqual(True, self.results["arg1"])
        self.assertEqual(None, self.results["arg2"])
        self.assertEqual("hello", self.results["arg3"])

    def test_use_settings(self):
        command = SampleScript(self.results)
        command.run(["-c", "hello"], settings={"arg1": False})
        self.assertTrue(self.results)
        self.assertEqual(False, self.results["arg1"])
        self.assertEqual(None, self.results["arg2"])
        self.assertEqual("hello", self.results["arg3"])

    def test_conflicts(self):
        command = SampleScript(self.results)
        self.assertRaises(ErrorEncountered, command.run, ("-a", "-b"))



