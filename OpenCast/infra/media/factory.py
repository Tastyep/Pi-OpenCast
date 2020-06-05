from pathlib import Path

from .player_wrapper import PlayerWrapper


class MediaFactory:
    def __init__(self, vlc_instance, downloader_executor):
        self._downloader_executor = downloader_executor
        self._vlc = vlc_instance

    def make_player(self, *args):
        return PlayerWrapper(self._vlc, *args)
