from test.util import TestCase

from OpenCast.domain.model.entity import Entity


class EntityTest(TestCase):
    def setUp(self):
        self.entity = Entity(None)

    def test_construction(self):
        self.assertEqual(None, self.entity.id)
        self.assertEqual(0, self.entity.version)
        self.assertEmpty(self.entity.release_events())

    def test_json(self):
        json = self.entity.to_dict()
        self.assertEqual({"_id": None, "_version": 0}, json)
