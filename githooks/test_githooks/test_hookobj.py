from unittest2 import TestCase
from pykfs.githooks.hookobj import GitHook
from mock import Mock, patch
import logging


class GitHookDummy(GitHook):
    hookname = "dummy"
    logger = logging.getLogger("dummyhookobj")
    actions = ["dummy_action_1", "dummy_action_2"]

    def __init__(self, *args, **kwargs):
        self._setup_logging = Mock()
        GitHook.__init__(self, *args, **kwargs)
        self.dummy_action_1 = Mock()
        self.dummy_action_2 = Mock()
        self._get_repo_info = Mock()


class TestGitHook(TestCase):

    def test_catches_exception(self):
        obj = GitHookDummy(Mock())
        for func in '_initialize', '_do_actions':
            with patch.object(obj, func) as mockfunc:
                mockfunc.side_effect=Exception
                obj()

    def test_invalid_setting(self):
        settings = {'dummy_action_1': True, 'dummy_action_3': True}
        obj = GitHookDummy(settings=settings)
        self.assertRaisesRegexp(TypeError, "invalid settings", obj._initialize)

    def test_run_action(self):
        settings = {'dummy_action_1': True}
        obj = GitHookDummy(settings=settings)
        obj()
        self.assertEqual(obj.dummy_action_1.call_count, 1)
        self.assertEqual(obj.dummy_action_2.call_count, 0)

    def test_irc(self):
        pass
