""" Module in charge of registering application services """

from OpenCast.app.service.album import AlbumService
from OpenCast.app.service.player import PlayerService
from OpenCast.app.service.playlist import PlaylistService
from OpenCast.app.service.video import VideoService


class ServiceModule:
    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        self._player_service = PlayerService(
            app_facade, data_facade, infra_facade.media_factory
        )
        self._video_service = VideoService(
            app_facade, service_factory, data_facade, infra_facade.media_factory
        )
        self._playlist_service = PlaylistService(
            app_facade, service_factory, data_facade
        )
        self._album_service = AlbumService(app_facade, service_factory, data_facade)
