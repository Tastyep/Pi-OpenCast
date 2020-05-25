from .ffmpeg_wrapper import FFmpegWrapper
from .server import Server
from .video_downloader import VideoDownloader


class IoFactory:
    def __init__(self, downloader_executor):
        self._downloader_executor = downloader_executor

    def make_ffmpeg_wrapper(self, *args):
        return FFmpegWrapper(*args)

    def make_server(self, *args):
        return Server(*args)

    def make_video_downloader(self, *args):
        return VideoDownloader(self._downloader_executor, *args)
