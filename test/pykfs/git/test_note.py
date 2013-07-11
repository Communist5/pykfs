import unittest2
import pykfs.git.note as gitnote
import logging


class TestGitNote(unittest2.TestCase):

    def test_is_valid_label_true(self):
        labels = ['foo', 'foo_bar', 'fooBar']
        for label in labels:
            self.assertTrue(gitnote._is_valid_label(label),
                            "'{0}' is not a valid label as expected".format(label))

    def test_start_re_match(self):
        tests = [
            {'message': ' <foo>bar', 'label': 'foo', 'rest': 'bar'},
            {'message': 'foo bar /dfds <foo>  note   \nhere \n </foo>',
             'label': 'foo',
             'rest': '  note   \nhere \n </foo>'}
        ]
        for test in tests:
            match = gitnote.START_NOTE_RE.match(test['message'])
            self.assertTrue(match, "unable to match message '{0}'".format(test['message']))
            self.assertEquals(test['label'], match.group('label'))
            self.assertEquals(test['rest'], match.group('rest'))


    def test_getnotes_blank(self):
        actual = gitnote.get_notes_from_message("")
        expected = {}
        self.assertEquals(expected, actual)

    def test_getnotes_one_note(self):
        message = "foo bar /dfds <foo>  note   \nhere \n </foo>"
        actual = gitnote.get_notes_from_message(message)
        expected = {'foo': ['note here']}
        self.assertEquals(expected, actual)

    def test_getnotes_many_notes(self):
        message = "<foo>note1</foo><bar>note2</bar><foo>note3</foo>"
        actual = gitnote.get_notes_from_message(message)
        expected = {'foo': ['note1', 'note3'], 'bar': ['note2']}
        self.assertEquals(expected, actual)

    def test_getnotes_different_closing(self):
        message = "<foo>note1</bar>"
        self.assertRaisesRegexp(gitnote.GitNoteException,
                                "mismatched label",
                                gitnote.get_notes_from_message,
                                message
                                )

    def test_getnotes_invalid_label(self):
        message = "<foo1></foo1>"
        self.assertRaisesRegexp(gitnote.GitNoteException,
                                "invalid",
                                gitnote.get_notes_from_message,
                                message
                                )
