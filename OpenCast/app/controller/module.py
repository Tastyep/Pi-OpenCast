""" Module in charge of registering application controllers """

from OpenCast.app.controller.player import PlayerController
from OpenCast.app.controller.player_monitor import PlayerMonitController
from OpenCast.app.controller.playlist_monitor import PlaylistMonitController
from OpenCast.app.controller.root_monitor import RootMonitController
from OpenCast.app.controller.video_monitor import VideoMonitController

from OpenCast.app.controller.album_monitor import AlbumMonitController  # isort: skip
from OpenCast.app.controller.artist_monitor import ArtistMonitController  # isort: skip


class ControllerModule:
    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        self._root_monitor = RootMonitController(app_facade, infra_facade)
        self._player_monitor = PlayerMonitController(
            app_facade, infra_facade, data_facade, service_factory
        )
        self._video_monitor = VideoMonitController(
            app_facade, infra_facade, data_facade
        )
        self._playlist_monitor = PlaylistMonitController(
            app_facade, infra_facade, data_facade
        )
        self._album_monitor = AlbumMonitController(
            app_facade, infra_facade, data_facade
        )
        self._artist_monitor = ArtistMonitController(
            app_facade, infra_facade, data_facade
        )
        self._player_controller = PlayerController(
            app_facade, data_facade, service_factory
        )
