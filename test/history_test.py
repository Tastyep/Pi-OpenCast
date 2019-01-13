from RaspberryCast.history import History

from .util import TestCase


class HistoryTest(TestCase):
    def test_push(self):
        history = History()

        history.push(0)
        self.assertEqual(history.current_item(), 0)
        self.assertFalse(history.browsing())

    def test_push_duplicate(self):
        history = History([0, 1])

        history.push(1)
        self.assertEqual(history.current_item(), 0)

    def test_can_prev_success(self):
        history = History([0])

        self.assertTrue(history.can_prev())

    def test_can_prev_failure(self):
        history = History()

        self.assertFalse(history.can_prev())

    def test_prev_success(self):
        history = History([0, 1])

        self.assertTrue(history.prev())
        self.assertEqual(history.current_item(), 0)
        self.assertTrue(history.browsing())

        self.assertTrue(history.prev())
        self.assertEqual(history.current_item(), 1)
        self.assertTrue(history.browsing())

    def test_prev_failure(self):
        history = History()

        self.assertFalse(history.prev())
        self.assertFalse(history.browsing())

    def test_next_success(self):
        history = History([0, 1])

        self.assertTrue(history.prev())  # 0
        self.assertTrue(history.prev())  # 1

        self.assertTrue(history.next())  # 0
        self.assertEqual(history.current_item(), 0)
        self.assertTrue(history.browsing())

    def test_next_failure(self):
        history = History([0])

        self.assertFalse(history.next())
        self.assertEqual(history.current_item(), 0)
        self.assertFalse(history.browsing())

    def test_stop_browsing(self):
        history = History([0, 1])

        history.prev()  # 0
        history.prev()  # 1

        history.stop_browsing()
        self.assertEqual(history.current_item(), 0)
        self.assertFalse(history.browsing())
