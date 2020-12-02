from test.util import TestCase
from threading import RLock

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from OpenCast.domain.model.player import Player
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.repo.player import PlayerRepo


class PlayerRepositoryTest(TestCase):
    def setUp(self):
        database = TinyDB(storage=MemoryStorage)
        self.repo = PlayerRepo(database, RLock())
        self.player_id = IdentityService.id_player()
        self.queue_id = IdentityService.id_playlist()
        self.player = Player(self.player_id, self.queue_id)

    def test_get(self):
        self.assertEqual(None, self.repo.get_player())
        self.repo.create(self.player)
        self.assertEqual(self.player, self.repo.get_player())
