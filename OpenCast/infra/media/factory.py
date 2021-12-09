""" Factory for creating media processing objects """

from .downloader import Downloader
from .parser import VideoParser
from .player_wrapper import PlayerWrapper


class MediaFactory:
    def __init__(self, vlc_instance, downloader_executor, cache):
        self._downloader_executor = downloader_executor
        self._cache = cache
        self._vlc = vlc_instance

    def make_player(self, *args):
        return PlayerWrapper(self._vlc, *args)

    def make_downloader(self, *args):
        return Downloader(self._downloader_executor, self._cache, *args)

    def make_video_parser(self, *args):
        return VideoParser(self._vlc, *args)
