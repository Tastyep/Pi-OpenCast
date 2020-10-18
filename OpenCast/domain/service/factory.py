""" Factory for creating domain services """

from .player import QueueingService
from .source import SourceService
from .subtitle import SubtitleService


class ServiceFactory:
    """The domain service factory"""

    def __init__(self, infra_service_factory):
        """The domain service factory constructor

        Args:
            infra_service_factory: Unused at the moment
        """
        self._infra_service_factory = infra_service_factory

    def make_source_service(self, *args):
        return SourceService(*args)

    def make_subtitle_service(self, *args):
        return SubtitleService(self._infra_service_factory.make_file_service(), *args)

    def make_queueing_service(self, *args):
        return QueueingService(*args)
