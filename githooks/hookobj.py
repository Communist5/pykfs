import logging
import os
import sys
import getpass
import irc.client
from pykfs import gitlib


_LOGGING_DEFAULT={"level": logging.INFO,
                  "format": '- %(asctime)s - %(levelname)s - %(message)s',
                  "datefmt": '%Y-%m-%d %H:%M:%S',
                  "filemode": 'w'}


class GitHook(object):

    def __init__(self, settings):
        self.settings = settings
        self._unread_settings = self.settings.copy()
        self._setup_logging()

    def _setup_logging(self):
        self.log_settings = _LOGGING_DEFAULT.copy()
        self.log_settings.update(self.settings.pop("logging", {}))
        if 'filename' not in self.log_settings:
            raise TypeError("pykfs githooks require a logging filename")
        logging.basicConfig(**self.log_settings)
        self.logger = logging.getLogger(self.logger_name)

    def __call__(self):
        try:
            self._initialize()
            self.logger.info("{hookname} git hook started for repo {reponame}"
                             .format(hookname=self.hookname, reponame=
                             self.reponame))
            self._do_actions()
        except Exception as e:
            reporoot = getattr(self, 'reporoot', False) or 'unknown'
            message = ("Error encountered during '{name}' of repository "
                       "'{repopath}'.".format(name=self.hookname, repopath=
                       reporoot))
            self.logger.error(message)
            sys.stderr.write("{}\n".format(message))
            self.logger.exception(e)
            self.logger.error("Abandoning hook ...")
            return 1

    def _initialize(self):
        for func, message in [
                    (self._read_settings, "Reading settings ..."),
                    (self._parse_input, "Parsing input ..."),
                    (self._get_repo_info, "Gathering repo info ...")]:
                self.logger.info(message)
                func()

    def _read_settings(self):
        self.unread_settings = self.settings.copy()
        self.actions = {}
        for action in self.actions_available:
            self.actions[action] = self.unread_settings.pop(action, None)
        for invalid in self.unread_settings:
            raise TypeError("{hookname} got invalid settings element "
                            "'{invalid}'".format(hookname=self.hookname,
                            invalid=invalid))

    def _get_repo_info(self):
        self.dotgitdir = os.getcwd()
        self.logger.debug("Dotgitdir: {}".format(self.dotgitdir))
        self.reporoot, dotgit = os.path.split(self.dotgitdir)
        if dotgit != '.git':
            self.reporoot = self.dotgitdir
        self.logger.debug("Reporoot : {}".format(self.reporoot))
        _, self.reponame = os.path.split(self.reporoot)
        self.logger.debug("Reponame : {}".format(self.reporoot))
        self.user = getpass.getuser()

    def _parse_input(self):
        raise NotImplementedError()

    def _do_actions(self):
        for action, options in self.actions.items():
            if options:
                self.logger.info("Performing '{}' action ...")
                getattr(self, action)(**options)


class PostReceive(GitHook):
    logger_name = 'postreceive'
    hookname = 'post-receive'
    actions_available = ['irc', 'backup']

    def _parse_input(self):
        self.stdin = sys.stdin.read()
        self.oldhead, self.newhead, self.ref = self.stdin.split()
        self.branch_changed = self.ref.split('/')[-1]

    def _get_repo_info(self):
        GitHook._get_repo_info(self)
        self.commit_message = gitlib.commit_message(self.newhead,
                                                    cwd=self.reporoot)
        self.short_commit_message = self.commit_message.split('\n')[0]

    def irc(self, **kwargs):
        client = irc.client.IRC()
        server = client.server()
        channel = kwargs.pop('channel')
        for name in 'ircname', 'nickname', 'username':
            kwargs.setdefault(name, 'git')
        kwargs.setdefault('port', 6667)
        connection = server.connect(**kwargs)
        connection.join(channel)
        details = {'user': self.user,
                   'repo': self.reponame,
                   'sha': self.newhead[:7],
                   'branch': self.branch_changed,
                   'message': self.short_commit_message}
        line1 = ("[{repo}] Push received from '{user}' to branch '{branch}', "
                 "sha '{sha}'".format(**details))
        line2 = ("  {message}".format(**details))
        for line in line1, line2:
            connection.privmsg(channel, line)
            self.logger.info('IRC: {}'.format(line))
        connection.close()

