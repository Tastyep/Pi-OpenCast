from copy import deepcopy

from .memory_repository import MemoryRepository


class PlayerRepo(MemoryRepository):
    def __init__(self):
        super(PlayerRepo, self).__init__()

    def get_player(self):
        players = self.list()
        return deepcopy(players[0]) if len(players) > 0 else None
