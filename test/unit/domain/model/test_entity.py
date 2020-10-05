from dataclasses import dataclass
from test.util import TestCase
from unittest.mock import Mock

from marshmallow import Schema, fields

from OpenCast.domain.model import Id
from OpenCast.domain.model.entity import Entity
from OpenCast.domain.service.identity import IdentityService


class DumbEntitySchema(Schema):
    id = fields.UUID()


class DumbEntity(Entity):
    Schema = DumbEntitySchema

    @dataclass
    class Data:
        id: Id

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)


class EntityTest(TestCase):
    def setUp(self):
        self.entity_id = IdentityService.random()
        self.entity = DumbEntity(self.entity_id)

    def test_construction(self):
        self.assertEqual(self.entity_id, self.entity.id)
        self.assertEmpty(self.entity.release_events())

    def test_from_dict(self):
        entity_id = IdentityService.random()
        entity = DumbEntity.from_dict({"id": entity_id})
        self.assertEqual(entity_id, entity.id)
        self.assertEmpty(entity.release_events())

    def test_release_events(self):
        self.entity._record(Mock)
        events = self.entity.release_events()
        self.assertEqual(1, len(events))
        self.assertEqual([Mock], list(events[0].keys()))

    def test_to_dict(self):
        dict = self.entity.to_dict()
        self.assertEqual({"id": str(self.entity.id)}, dict)
