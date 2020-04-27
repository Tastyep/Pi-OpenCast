from .player import PlayerService
from .video import VideoService


class ServiceModule:
    def __init__(
        self, app_facade, data_facade, io_facade, media_facade, service_factory
    ):
        self._player_service = PlayerService(app_facade, data_facade, media_facade)
        self._video_service = VideoService(
            app_facade, data_facade, io_facade, service_factory
        )
