import unittest


class TestCase(unittest.TestCase):
    def assertEmpty(self, o):
        self.assertFalse(len(o) > 0)

    def assertNonEmpty(self, o):
        self.assertTrue(len(o) > 0)

    def assertListEqual(self, l1, l2):
        self.assertEqual(len(l1), len(l2))
        self.assertTrue(all(x1 == x2 for (x1, x2) in zip(l1, l2)))
