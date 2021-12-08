""" Handlers for album commands """

import structlog

from OpenCast.app.command import album as AlbumCmds
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.album import Album

from .service import Service


class AlbumService(Service):
    def __init__(self, app_facade, service_factory, data_facade, media_factory):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, AlbumCmds)

        self._observe_event(VideoEvt.VideoDeleted)
        self._observe_event(VideoEvt.VideoCreated)

        self._album_repo = data_facade.album_repo
        self._video_repo = data_facade.video_repo

        self._downloader = media_factory.make_downloader(app_facade.evt_dispatcher)
        self._source_service = service_factory.make_source_service(
            self._downloader, media_factory.make_video_parser()
        )

    # Command handler implementation
    def _delete_album(self, cmd):
        def impl(ctx):
            album = self._album_repo.get(cmd.model_id)
            album.delete()
            ctx.delete(album)

        self._start_transaction(self._album_repo, cmd.id, impl)

    # Event handler implementation

    def _video_created(self, evt):
        def create_album(ctx, metadata):
            album = Album(evt.album_id, metadata["album"], [evt.model_id], None)
            ctx.add(album)

        def update_album(ctx, album):
            album.add(evt.model_id)
            ctx.update(album)

        if not evt.album_id:
            return

        album = self._album_repo.get(evt.album_id)
        if album is None:
            metadata = self._source_service.pick_stream_metadata(evt.source)
            if metadata is None or metadata.get("album") is None:
                return

            self._start_transaction(self._album_repo, evt.id, create_album, metadata)
        else:
            self._start_transaction(self._album_repo, evt.id, update_album, album)

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
