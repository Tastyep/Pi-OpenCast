from pathlib import Path

from .player_wrapper import PlayerWrapper


class MediaFactory:
    def make_player(self, *args):
        return PlayerWrapper(*args)
