from .file_controller import FileController
from .player_monit_controller import PlayerMonitController


class ControllerModule:
    def __init__(self, app_facade, data_facade, io_facade):
        self._file_controller = FileController(app_facade, io_facade)
        self._player_monit_controller = PlayerMonitController(
            app_facade, data_facade, io_facade
        )
