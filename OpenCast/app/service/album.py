""" Handlers for album commands """

import structlog

from OpenCast.app.command import album as AlbumCmds
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.album import Album
from OpenCast.domain.service.identity import IdentityService

from .service import Service


class AlbumService(Service):
    def __init__(self, app_facade, service_factory, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, AlbumCmds)

        self._observe_event(VideoEvt.VideoDeleted)
        self._observe_event(VideoEvt.VideoCreated)

        self._album_repo = data_facade.album_repo
        self._video_repo = data_facade.video_repo

    # Command handler implementation
    def _delete_album(self, cmd):
        def impl(ctx):
            album = self._album_repo.get(cmd.model_id)
            album.delete()
            ctx.delete(album)

        self._start_transaction(self._album_repo, cmd.id, impl)

    # Event handler implementation

    def _video_created(self, evt):
        def create_album(ctx, album_id, video):
            album = Album(album_id, video.album, [video.id], None)
            ctx.add(album)

        def update_album(ctx, album, video):
            album.add(video.id)
            ctx.update(album)

        video = self._video_repo.get(evt.model_id)
        if not video.album:
            return

        album_id = IdentityService.id_album(video.album)
        album = self._album_repo.get(album_id)
        if album is None:
            self._start_transaction(
                self._album_repo, evt.id, create_album, album_id, video
            )
        else:
            self._start_transaction(
                self._album_repo, evt.id, update_album, album, video
            )

    def _video_deleted(self, evt):
        def impl(ctx):
            albums = self._album_repo.list_containing(evt.model_id)
            for album in albums:
                album.remove(evt.model_id)
                if album.empty():
                    album.delete()
                    ctx.delete(album)
                else:
                    ctx.update(album)

        self._start_transaction(self._album_repo, evt.id, impl)
