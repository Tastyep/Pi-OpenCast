from test.util import TestCase


class ModelTestCase(TestCase):
    def expect_events(self, model, *events):
        self.assertListEqual(list(events), list(model.release_events().keys()))
