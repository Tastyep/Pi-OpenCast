import unittest


class TestCase(unittest.TestCase):
    def assertEmpty(self, o):
        self.assertFalse(len(o) > 0)

    def assertNonEmpty(self, o):
        self.assertTrue(len(o) > 0)
