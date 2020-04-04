from .player_service import PlayerService


class ServiceModule(object):
    def __init__(self, app_facade, data_facade, io_facade, media_facade):
        self._player_service = PlayerService(
            app_facade, data_facade, io_facade, media_facade
        )
