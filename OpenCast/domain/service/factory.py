from .source import SourceService
from .subtitle import SubtitleService


class ServiceFactory:
    def make_source_service(self, *args):
        return SourceService(*args)

    def make_subtitle_service(self, *args):
        return SubtitleService(*args)
