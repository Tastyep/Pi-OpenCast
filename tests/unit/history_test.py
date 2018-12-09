import unittest

from RaspberryCast.history import History


class HistoryTest(unittest.TestCase):
    def setUp(self):
        self.history = History()

    def test_push(self):
        self.history.push(0)

        self.assertEqual(len(self.history), 1)
        self.assertEqual(self.history[0], 0)
        self.assertFalse(self.history.browsing())
