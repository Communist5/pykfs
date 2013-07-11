from pykfs.git.lib import commit_message
import re
import logging


LOGGER = logging.getLogger("pykfs.git.note")
START_NOTE_RE = re.compile("^.*?<(?P<label>\S*?)>(?P<rest>.*)$", flags=re.S)
END_NOTE_RE = re.compile("^(?P<note>.*?)</(?P<label>\S*?)>(?P<rest>.*)$", flags=re.S)


class GitNoteException(Exception):
    pass


def getnotes(sha, gitdir=None):
    message = commit_message(sha, gitdir=gitdir)
    notes = get_notes_from_message(message)
    LOGGER.debug(
        "Found {0} messages for sha '{1}'".format(sum([len(x) for x in notes.values()], sha))
    )
    return notes


def get_notes_from_message(message):
    match = re.match(START_NOTE_RE, message)
    notes = {}
    while match:
        label = match.group('label')
        rest = match.group('rest')
        LOGGER.debug("Found note label '{0}'".format(label))
        if not _is_valid_label(label):
            raise GitNoteException("Note label '{0}' is an invalid note label".format(label))
        endmatch = re.match(END_NOTE_RE, rest)
        if not endmatch:
            raise GitNoteException("Note with label '{0}' unclosed".format(label))
        note = " ".join(endmatch.group('note').split())
        endlabel = endmatch.group('label')
        rest = endmatch.group('rest')
        if not label == endlabel:
            raise GitNoteException(
                "Note with label '{0}' closed by mismatched label '{1}'".format(label, endlabel)
            )
            LOGGER.debug("Saving note '{0}: {1}'".format(label, note))
        _addnote(notes, label, note)
        match = re.match(START_NOTE_RE, rest)
    return notes


def _addnote(notes, label, note):
    if label not in notes:
        notes[label] = []
    notes[label].append(note)


def _is_valid_label(label):
    return bool(re.match("^[a-z_]+$", label, flags=re.I))
