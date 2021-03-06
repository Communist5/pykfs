import logging
import os
import sys
import getpass
import irc.client
import pykfs.git.lib as gitlib
import pykfs.git.note as gitnote


_LOGGING_DEFAULT = {
    "level": logging.INFO,
    "format": '- %(asctime)s - %(levelname)s - %(message)s',
    "datefmt": '%Y-%m-%d %H:%M:%S',
    "filemode": 'w'
}


class GitHook(object):

    def __init__(self, settings):
        self.print_stderr = False
        self.settings = settings
        self._unread_settings = self.settings.copy()
        self._setup_logging()

    def _setup_logging(self):
        self.log_settings = _LOGGING_DEFAULT.copy()
        self.log_settings.update(self._unread_settings.pop("logging", {}))
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
            if self.print_stderr:
                sys.stderr.write("{}\n".format(message))
            raise

    def _initialize(self):
        for func, message in [
                    (self._read_settings, "Reading settings ..."),
                    (self._parse_input, "Parsing input ..."),
                    (self._get_repo_info, "Gathering repo info ...")]:
                self.logger.info(message)
                func()

    def _read_settings(self):
        self.actions = {}
        self.stdin = self._unread_settings.pop('stdin', None)
        self.print_stderr = self._unread_settings.pop('print_stderr', True)
        if self.stdin is None:
            self.stdin = sys.stdin.read()
        for action in self.actions_available:
            self.actions[action] = self._unread_settings.pop(action, None)
        for invalid in self._unread_settings:
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
                self.logger.info("Performing '{}' action ...".format(action))
                getattr(self, action)(**options)


class PostReceive(GitHook):
    logger_name = 'postreceive'
    hookname = 'post-receive'
    actions_available = ['irc']

    def _parse_input(self):
        self.oldhead, self.newhead, self.ref = self.stdin.split()
        self.branch_changed = self.ref.split('/')[-1]

    def _get_repo_info(self):
        GitHook._get_repo_info(self)
        self.commit_message = gitlib.commit_message(self.newhead,
                                                    gitdir=self.dotgitdir)
        self.short_commit_message = self.commit_message.split('\n')[0]

    def irc(self, **kwargs):
        client = irc.client.IRC()
        server = client.server()
        channel = kwargs.pop('channel')
        for name in 'ircname', 'nickname', 'username':
            kwargs.setdefault(name, 'git')
        kwargs.setdefault('port', 6667)
        self.logger.debug("Connection Info:")
        self.logger.debug(kwargs)
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


class PreReceive(GitHook):
    logger_name = 'prereceive'
    hookname = 'pre-receive'
    actions_available = ['validate_notes']

    def _parse_input(self):
        self.oldhead, self.newhead, self.ref = self.stdin.split()
        self.branch_changed = self.ref.split('/')[-1]

    def _get_repo_info(self):
        GitHook._get_repo_info(self)
        self.commit_message = gitlib.commit_message(self.newhead,
                                                    gitdir=self.dotgitdir)
        self.short_commit_message = self.commit_message.split('\n')[0]

    def validate_notes(self, valid_labels=None):
        validate_notes(self.commit_message, valid_labels)


class CommitMsg(GitHook):
    logger_name = 'commitmsg'
    hookname = 'commit-msg'
    actions_available = ['validate_notes']

    def _parse_input(self):
        self.message = ""
        with open(sys.argv[1]) as f:
            line = f.readline().strip()
            if line and line[0] != '#':
                self.message += line
        self.logger.debug("Read in message: '{0}'".format(self.message))

    def validate_notes(self, valid_labels=None):
        validate_notes(self.message, valid_labels)


def validate_notes(message, valid_labels=None):
    notes = gitnote.get_notes_from_message(message)
    if valid_labels:
        for label in notes:
            if label not in valid_labels:
                raise gitnote.GitNoteException(
                    "Git note label '{0}' not recognized for this repository".format(label)
                )
