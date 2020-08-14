from .player import PlayerController
from .player_monitor import PlayerMonitController
from .video_monitor import VideoMonitController


class ControllerModule:
    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        self._player_monitor = PlayerMonitController(
            app_facade, infra_facade, data_facade, service_factory
        )
        self._video_monitor = VideoMonitController(
            app_facade, infra_facade, data_facade
        )
        self._player_controller = PlayerController(app_facade, data_facade)
