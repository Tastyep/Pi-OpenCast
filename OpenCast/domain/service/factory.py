from .source import SourceService
from .subtitle import SubtitleService


class ServiceFactory:
    def make_source_service(self, downloader):
        return SourceService(downloader)

    def make_subtitle_service(self, ffmpeg_wrapper):
        return SubtitleService(ffmpeg_wrapper)
