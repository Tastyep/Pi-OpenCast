from .file_controller import FileController
from .player_controller import PlayerController


class ControllerModule(object):
    def __init__(self, app_facade, server):
        cmd_dispatcher = app_facade.cmd_dispatcher()

        self._file_controller = FileController(cmd_dispatcher, server)
        self._player_controller = PlayerController(cmd_dispatcher, server)
