from test.util import TestCase

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from OpenCast.domain.model.player import Player
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.repo.player import PlayerRepo


class RepositoryTest(TestCase):
    def setUp(self):
        database = TinyDB(storage=MemoryStorage)
        self.repo = PlayerRepo(database)
        self.player_id = IdentityService.id_player()
        self.player = Player(self.player_id)

    def test_get(self):
        self.assertEqual(None, self.repo.get_player())
        self.repo.create(self.player)
        self.assertEqual(self.player, self.repo.get_player())
