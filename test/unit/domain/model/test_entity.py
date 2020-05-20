from test.util import TestCase

from OpenCast.domain.model.entity import Entity


class EntityTest(TestCase):
    def test_construction(self):
        entity_id = None
        entity = Entity(entity_id)
        self.assertEqual(entity_id, entity.id)
        self.assertEqual(0, entity.version)
        self.assertEmpty(entity.release_events())
