from test.util import TestCase
from unittest.mock import Mock

from OpenCast.domain.model.entity import Entity


class EntityTest(TestCase):
    def setUp(self):
        self.entity = Entity(None)

    def test_construction(self):
        self.assertEqual(None, self.entity.id)
        self.assertEqual(0, self.entity.version)
        self.assertEmpty(self.entity.release_events())

    def test_update_version(self):
        self.entity.update_version()
        self.assertEqual(1, self.entity.version)

    def test_release_events(self):
        self.entity._record(Mock)
        events = self.entity.release_events()
        self.assertEqual(1, len(events))
        self.assertEqual([Mock], list(events[0].keys()))

    def test_json(self):
        json = self.entity.to_dict()
        self.assertEqual({"_id": None, "_version": 0}, json)
