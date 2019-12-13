from .player_service import PlayerService


class ServiceModule(object):
    def __init__(self, app_facade, player, downloader):
        cmd_dispatcher = app_facade.cmd_dispatcher()
        self._player_service = PlayerService(cmd_dispatcher, player, downloader)
