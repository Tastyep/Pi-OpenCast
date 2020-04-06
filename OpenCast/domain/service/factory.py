from .playlist import PlaylistService
from .subtitle import SubtitleService


class ServiceFactory:
    def make_playlist_service(self, downloader):
        return PlaylistService(downloader)

    def make_subtitle_service(self, ffmpeg_wrapper):
        return SubtitleService(ffmpeg_wrapper)
