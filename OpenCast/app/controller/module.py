from .file import FileController
from .player_monitor import PlayerMonitController


class ControllerModule:
    def __init__(self, app_facade, data_facade, io_facade):
        self._file_controller = FileController(app_facade, io_facade)
        self._player_monitor = PlayerMonitController(app_facade, data_facade, io_facade)
