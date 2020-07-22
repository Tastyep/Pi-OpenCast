from test.util import TestCase


class ModelTestCase(TestCase):
    def expect_events(self, model, *events):
        model_events = [evtcls for event in model.release_events() for evtcls in event]
        self.assertListEqual(list(events), model_events)
