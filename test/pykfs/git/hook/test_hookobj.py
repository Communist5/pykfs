from unittest2 import TestCase
from pykfs.git.hook.hookobj import GitHook
from mock import Mock
import logging


class GitHookDummy(GitHook):
    hookname = "dummy"
    actions_available = ["dummy_action_1", "dummy_action_2"]

    def __init__(self, *args, **kwargs):
        self._setup_logging = Mock()
        GitHook.__init__(self, *args, **kwargs)
        self.dummy_action_1 = Mock()
        self.dummy_action_2 = Mock()
        self._get_repo_info = Mock()
        self.logger = logging.getLogger("dummyhookobj")
        self.reponame = "foo"

    def _parse_input(self):
        pass

    def _get_repo_info(self):
        self.reponame = 'foo'


class TestGitHook(TestCase):

    def test_invalid_setting(self):
        settings = {'dummy_action_1': {},
                    'dummy_action_3': {},
                    'stdin': "",
                    'print_stderr': False}
        obj = GitHookDummy(settings=settings)
        self.assertRaisesRegexp(TypeError, "invalid settings", obj._initialize)

    def test_run_action(self):
        settings = {'dummy_action_1': {"foo": "bar"},
                    'stdin': "",
                    'print_stderr': False}
        obj = GitHookDummy(settings=settings)
        obj()
        self.assertEqual(obj.dummy_action_1.call_count, 1)
        self.assertEqual(obj.dummy_action_2.call_count, 0)

    def test_irc(self):
        pass
