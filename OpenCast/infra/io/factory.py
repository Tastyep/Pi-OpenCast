from .ffmpeg_wrapper import FFmpegWrapper
from .server import Server
from .downloader import Downloader


class IoFactory:
    def __init__(self, downloader_executor):
        self._downloader_executor = downloader_executor

    def make_ffmpeg_wrapper(self, *args):
        return FFmpegWrapper(*args)

    def make_server(self, *args):
        return Server(*args)

    def make_downloader(self, *args):
        return Downloader(self._downloader_executor, *args)
