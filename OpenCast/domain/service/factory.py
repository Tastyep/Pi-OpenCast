from .source import SourceService
from .subtitle import SubtitleService


class ServiceFactory:
    def __init__(self, infra_service_factory):
        self._infra_service_factory = infra_service_factory

    def make_source_service(self, *args):
        return SourceService(*args)

    def make_subtitle_service(self, *args):
        return SubtitleService(
            self._infra_service_factory.make_subtitle_converter(), *args
        )
