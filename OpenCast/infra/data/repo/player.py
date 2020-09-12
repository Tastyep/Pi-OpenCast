""" Player repository """

from copy import deepcopy

from .memory import MemoryRepo


class PlayerRepo(MemoryRepo):
    def __init__(self):
        super().__init__()

    def get_player(self):
        players = self.list()
        return deepcopy(players[0]) if len(players) > 0 else None
