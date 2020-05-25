from .file import FileController
from .player_monitor import PlayerMonitController


class ControllerModule:
    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        self._file_controller = FileController(app_facade, infra_facade.server)
        self._player_monitor = PlayerMonitController(
            app_facade, infra_facade, data_facade, service_factory
        )
