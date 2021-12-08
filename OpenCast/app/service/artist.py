""" Handlers for artist commands """

import structlog

from OpenCast.app.command import artist as ArtistCmds
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.artist import Artist

from .service import Service


class ArtistService(Service):
    def __init__(self, app_facade, service_factory, data_facade, media_factory):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, ArtistCmds)

        self._observe_event(VideoEvt.VideoDeleted)
        self._observe_event(VideoEvt.VideoCreated)

        self._artist_repo = data_facade.artist_repo
        self._video_repo = data_facade.video_repo

        self._downloader = media_factory.make_downloader(app_facade.evt_dispatcher)
        self._source_service = service_factory.make_source_service(
            self._downloader, media_factory.make_video_parser()
        )

    # Command handler implementation
    def _delete_artist(self, cmd):
        def impl(ctx):
            artist = self._artist_repo.get(cmd.model_id)
            artist.delete()
            ctx.delete(artist)

        self._start_transaction(self._artist_repo, cmd.id, impl)

    # Event handler implementation

    def _video_created(self, evt):
        def create_artist(ctx, metadata):
            artist = Artist(evt.artist_id, metadata["artist"], [evt.model_id], None)
            ctx.add(artist)

        def update_artist(ctx, artist):
            artist.add(evt.model_id)
            ctx.update(artist)

        if not evt.artist_id:
            return

        artist = self._artist_repo.get(evt.artist_id)
        if artist is None:
            metadata = self._source_service.pick_stream_metadata(evt.source)
            if metadata is None or metadata.get("artist") is None:
                return

            self._start_transaction(self._artist_repo, evt.id, create_artist, metadata)
        else:
            self._start_transaction(self._artist_repo, evt.id, update_artist, artist)

    def _video_deleted(self, evt):
        def impl(ctx):
            artists = self._artist_repo.list_containing(evt.model_id)
            for artist in artists:
                artist.remove(evt.model_id)
                if artist.empty():
                    artist.delete()
                    ctx.delete(artist)
                else:
                    ctx.update(artist)

        self._start_transaction(self._artist_repo, evt.id, impl)
