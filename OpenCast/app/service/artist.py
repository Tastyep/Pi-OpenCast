""" Handlers for artist commands """

import structlog

from OpenCast.app.command import artist as ArtistCmds
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.artist import Artist
from OpenCast.domain.service.identity import IdentityService

from .service import Service


class ArtistService(Service):
    def __init__(self, app_facade, service_factory, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, ArtistCmds)

        self._observe_event(VideoEvt.VideoDeleted)
        self._observe_event(VideoEvt.VideoCreated)

        self._artist_repo = data_facade.artist_repo
        self._video_repo = data_facade.video_repo

    # Command handler implementation
    def _delete_artist(self, cmd):
        def impl(ctx):
            artist = self._artist_repo.get(cmd.model_id)
            artist.delete()
            ctx.delete(artist)

        self._start_transaction(self._artist_repo, cmd.id, impl)

    # Event handler implementation

    def _video_created(self, evt):
        def create_artist(ctx, artist_id, video):
            artist = Artist(artist_id, video.artist, [video.id], None)
            ctx.add(artist)

        def update_artist(ctx, artist, video):
            artist.add(video.id)
            ctx.update(artist)

        video = self._video_repo.get(evt.model_id)
        if not video.artist:
            return

        artist_id = IdentityService.id_artist(video.artist)
        artist = self._artist_repo.get(artist_id)
        if artist is None:
            self._start_transaction(
                self._artist_repo, evt.id, create_artist, artist_id, video
            )
        else:
            self._start_transaction(
                self._artist_repo, evt.id, update_artist, artist, video
            )

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
