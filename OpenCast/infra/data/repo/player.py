""" Player repository """

from OpenCast.domain.model.player import Player

from .repository import Repository


class PlayerRepo(Repository):
    def __init__(self, database):
        super().__init__(database, Player)

    def get_player(self):
        collection = self.list()
        return collection[0] if collection else None
