from dataclasses import dataclass
from test.util import TestCase

from marshmallow import Schema, fields, post_load
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from OpenCast.domain.model import Id
from OpenCast.domain.model.entity import Entity
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.repo.error import RepoError
from OpenCast.infra.data.repo.repository import Repository


class TestEntitySchema(Schema):
    id = fields.UUID()
    name = fields.String()

    @post_load
    def make_test_entity(self, data, **_):
        return TestEntity(**data)


class TestEntity(Entity):
    Schema = TestEntitySchema

    @dataclass
    class Data:
        id: Id
        name: str

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)

    @property
    def name(self):
        return self._data.name

    @name.setter
    def name(self, value):
        self._data.name = value


class RepositoryTest(TestCase):
    def setUp(self):
        database = TinyDB(storage=MemoryStorage)
        self.repo = Repository(database, TestEntitySchema())
        self.entity = TestEntity(IdentityService.random(), "test")

    def test_create(self):
        self.repo.create(self.entity)
        self.assertListEqual([self.entity], self.repo.list())

    def test_create_existing(self):
        self.repo.create(self.entity)
        with self.assertRaises(RepoError) as ctx:
            self.repo.create(self.entity)
        self.assertEqual(
            f"cannot create: '{self.entity}' already exists", str(ctx.exception)
        )

    def test_update(self):
        self.repo.create(self.entity)
        self.entity.name = "UPDATED"
        self.repo.update(self.entity)
        entity = self.repo.get(self.entity.id)
        self.assertEqual("UPDATED", entity.name)

    def test_update_nonexistent(self):
        with self.assertRaises(RepoError) as ctx:
            self.repo.update(self.entity)
        self.assertEqual(
            f"cannot update: '{self.entity}' doesn't exist", str(ctx.exception)
        )

    def test_delete(self):
        self.repo.create(self.entity)
        self.repo.delete(self.entity)
        self.assertListEqual([], self.repo.list())

    def test_list(self):
        self.repo.create(self.entity)
        entity_list = self.repo.list()
        self.assertEqual([self.entity], entity_list)
        self.assertNotEqual(id(self.entity), id(entity_list[0]))

    def test_list_filtered(self):
        entities = [TestEntity(IdentityService.random(), f"{i}") for i in range(5)]
        for entity in entities:
            self.repo.create(entity)
        entity_list = self.repo.list([entities[0].id, entities[2].id])
        self.assertEqual([entities[0], entities[2]], entity_list)

    def test_get(self):
        self.repo.create(self.entity)
        repo_entity = self.repo.get(self.entity.id)
        self.assertEqual(self.entity, repo_entity)
        self.assertNotEqual(id(self.entity), id(repo_entity))

    def test_get_nonexistent(self):
        self.assertEqual(None, self.repo.get(self.entity.id))

    def test_exists(self):
        self.assertFalse(self.repo.exists(self.entity.id))
        self.repo.create(self.entity)
        self.assertTrue(self.repo.exists(self.entity.id))
