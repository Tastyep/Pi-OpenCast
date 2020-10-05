""" Handlers for playlist commands """

import structlog

from OpenCast.app.command import playlist as playlist_cmds
from OpenCast.domain.model.playlist import Playlist

from .service import Service


class PlaylistService(Service):
    def __init__(self, app_facade, service_factory, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, self, playlist_cmds)
        self._playlist_repo = data_facade.playlist_repo

    # Command handler implementation
    def _create_playlist(self, cmd):
        def impl(ctx):
            playlist = Playlist(cmd.model_id, cmd.name, cmd.ids)
            ctx.add(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)

    def _delete_playlist(self, cmd):
        def impl(ctx):
            playlist = self._playlist_repo.get(cmd.model_id)
            playlist.delete()
            ctx.delete(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)

    def _rename_playlist(self, cmd):
        def impl(ctx):
            playlist = self._playlist_repo.get(cmd.model_id)
            playlist.name = cmd.name
            ctx.update(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)

    def _update_playlist_content(self, cmd):
        def impl(ctx):
            playlist = self._playlist_repo.get(cmd.model_id)
            playlist.ids = cmd.ids
            ctx.update(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)
