from test.util import TestCase
from unittest.mock import Mock

from OpenCast.infra.data.repo.context import Context


class ContextTest(TestCase):
    def setUp(self):
        self.repo = Mock()
        self.context = Context(self.repo)
        self.entity = "toto"

    def test_add(self):
        self.context.add(self.entity)
        self.assertListEqual([self.entity], self.context.entities())
        self.context.commit()
        self.repo.create.assert_called_once_with(self.entity)

    def test_update(self):
        self.context.update(self.entity)
        self.assertListEqual([self.entity], self.context.entities())
        self.context.commit()
        self.repo.update.assert_called_once_with(self.entity)

    def test_delete(self):
        self.context.delete(self.entity)
        self.assertListEqual([self.entity], self.context.entities())
        self.context.commit()
        self.repo.delete.assert_called_once_with(self.entity)
