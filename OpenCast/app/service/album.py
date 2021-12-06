""" Handlers for album commands """

import structlog

from OpenCast.app.command import album as AlbumCmds
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.album import Album

from .service import Service


class AlbumService(Service):
    def __init__(self, app_facade, service_factory, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, AlbumCmds)

        self._observe_event(VideoEvt.VideoDeleted)

        self._album_repo = data_facade.album_repo

    # Command handler implementation
    def _create_album(self, cmd):
        def impl(ctx):
            album = Album(cmd.model_id, cmd.name, cmd.ids, cmd.thumbnail)
            ctx.add(album)

        self._start_transaction(self._album_repo, cmd.id, impl)

    def _delete_album(self, cmd):
        def impl(ctx):
            album = self._album_repo.get(cmd.model_id)
            album.delete()
            ctx.delete(album)

        self._start_transaction(self._album_repo, cmd.id, impl)

    def _update_album_videos(self, cmd):
        def impl(ctx):
            album = self._album_repo.get(cmd.model_id)
            album.ids = cmd.ids
            ctx.update(album)

        self._start_transaction(self._album_repo, cmd.id, impl)

    # Event handler implementation

    def _video_deleted(self, evt):
        def impl(ctx):
            albums = self._album_repo.list_containing(evt.model_id)
            for album in albums:
                album.remove(evt.model_id)
                ctx.update(album)

        self._start_transaction(self._album_repo, evt.id, impl)
