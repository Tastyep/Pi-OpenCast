from .server import Server
from .video_downloader import VideoDownloader


class IoFactory:
    def make_server(self):
        return Server()

    def make_video_downloader(self):
        return VideoDownloader()
