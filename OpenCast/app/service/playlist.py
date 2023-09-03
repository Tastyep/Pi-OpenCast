""" Handlers for playlist commands """

import structlog

from OpenCast.app.command import playlist as playlist_cmds
from OpenCast.config import settings
from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.playlist import Playlist
from OpenCast.domain.service.playlist import shrink_playlist

from .service import Service


class PlaylistService(Service):
    def __init__(self, app_facade, service_factory, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, playlist_cmds)

        self._observe_event(VideoEvt.VideoDeleted)
        self._observe_event(PlaylistEvt.PlaylistDeleted)

        self._playlist_repo = data_facade.playlist_repo
        self._player_repo = data_facade.player_repo
        self._queueing_service = service_factory.make_queueing_service(
            data_facade.player_repo, data_facade.playlist_repo, data_facade.video_repo
        )

    # Command handler implementation
    def _create_playlist(self, cmd):
        def impl(ctx):
            playlist = Playlist(cmd.model_id, cmd.name, cmd.ids, cmd.generated)
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
            ids = self._queueing_service.queue(playlist, cmd.video_id, cmd.queue_front)

            player = self._player_repo.get_player()
            ids = shrink_playlist(
                ids, settings["player.queue.max_size"], [player.video_id]
            )

            playlist.ids = ids
            ctx.update(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)

    def _update_playlist_content(self, cmd):
        def impl(ctx):
            playlist = self._playlist_repo.get(cmd.model_id)
            playlist_ids = cmd.ids

            player = self._player_repo.get_player()
            if playlist.id == player.queue:
                playlist_ids = shrink_playlist(
                    playlist_ids, settings["player.queue.max_size"], [player.video_id]
                )

            playlist.ids = playlist_ids
            ctx.update(playlist)

        self._start_transaction(self._playlist_repo, cmd.id, impl)

    # Event handler implementation

    def _playlist_deleted(self, evt):
        def impl(ctx):
            home_playlist = self._playlist_repo.get(HOME_PLAYLIST.id)
            for video_id in evt.ids:
                if video_id in home_playlist.ids:
                    continue
                home_playlist.ids = self._queueing_service.queue(
                    home_playlist, video_id, front=False
                )
            ctx.update(home_playlist)

        self._start_transaction(self._playlist_repo, evt.id, impl)

    def _video_deleted(self, evt):
        def impl(ctx):
            playlists = self._playlist_repo.list_containing(evt.model_id)
            for playlist in playlists:
                playlist.remove(evt.model_id)
                ctx.update(playlist)

        self._start_transaction(self._playlist_repo, evt.id, impl)
