from test.util import TestCase
from unittest.mock import Mock
from uuid import uuid4

from OpenCast.domain.model.entity import Entity
from OpenCast.infra.data.repo.error import RepoError
from OpenCast.infra.data.repo.memory import MemoryRepo


class MemoryRepoTest(TestCase):
    def setUp(self):
        self.repo = MemoryRepo()
        self.entity = Entity(uuid4())

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
        entity_list = self.repo.list()
        self.assertEqual(1, len(entity_list))

        self.repo.update(self.entity)
        self.assertGreater(self.entity.version, entity_list[0].version)

    def test_update_nonexistent(self):
        with self.assertRaises(RepoError) as ctx:
            self.repo.update(self.entity)
        self.assertEqual(
            f"cannot update: '{self.entity}' doesn't exist", str(ctx.exception)
        )

    def test_update_outdated(self):
        self.repo.create(self.entity)
        old_entity = self.repo.list()[0]
        self.repo.update(self.entity)

        with self.assertRaises(RepoError) as ctx:
            self.repo.update(old_entity)
        self.assertEqual(
            f"cannot update: '{old_entity}' is outdated", str(ctx.exception)
        )

    def test_delete(self):
        self.repo.create(self.entity)
        self.repo.delete(self.entity)
        self.assertListEqual([], self.repo.list())

    def test_delete_nonexistent(self):
        with self.assertRaises(RepoError) as ctx:
            self.repo.delete(self.entity)
        self.assertEqual(
            f"cannot delete: '{self.entity}' doesn't exist", str(ctx.exception)
        )

    def test_list(self):
        self.repo.create(self.entity)
        entity_list = self.repo.list()
        self.assertEqual(1, len(entity_list))
        self.assertNotEqual(id(self.entity), id(entity_list[0]))

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
