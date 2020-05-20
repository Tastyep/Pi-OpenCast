from .ffmpeg_wrapper import FFmpegWrapper
from .server import Server
from .video_downloader import VideoDownloader


class IoFactory:
    def make_ffmpeg_wrapper(self, *args):
        return FFmpegWrapper(*args)

    def make_server(self, *args):
        return Server(*args)

    def make_video_downloader(self, *args):
        return VideoDownloader(*args)
