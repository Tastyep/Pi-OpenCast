""" Handlers for playlist commands """

import structlog

from OpenCast.app.command import playlist as playlist_cmds
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.playlist import Playlist

from .service import Service


class PlaylistService(Service):
    def __init__(self, app_facade, service_factory, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, playlist_cmds)

        self._observe_event(VideoEvt.VideoDeleted)

        self._playlist_repo = data_facade.playlist_repo
        self._queueing_service = service_factory.make_queueing_service(
            data_facade.player_repo, data_facade.playlist_repo
        )

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

    def _queue_video(self, cmd):
        def impl(ctx):
            playlist = self._playlist_repo.get(cmd.model_id)
            ids = self._queueing_service.queue(
                playlist, cmd.video_id, cmd.queue_front, cmd.prev_video_id
            )
            playlist.ids = ids
            ctx.update(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)

    def _update_playlist_content(self, cmd):
        def impl(ctx):
            playlist = self._playlist_repo.get(cmd.model_id)
            playlist.ids = cmd.ids
            ctx.update(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)

    # Event handler implementation

    def _video_deleted(self, evt):
        def impl(ctx):
            playlists = self._playlist_repo.list_containing(evt.model_id)
            for playlist in playlists:
                playlist.remove(evt.model_id)
                ctx.update(playlist)

        self._start_transaction(self._playlist_repo, evt.id, impl)
