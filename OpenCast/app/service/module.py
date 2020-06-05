from .player import PlayerService
from .video import VideoService


class ServiceModule:
    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        self._player_service = PlayerService(
            app_facade, data_facade, infra_facade.media_factory
        )
        self._video_service = VideoService(
            app_facade, service_factory, data_facade, infra_facade.media_factory
        )
