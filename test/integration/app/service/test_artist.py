from OpenCast.app.command import artist as Cmd
from OpenCast.domain.event import artist as Evt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class ArtistServiceTest(ServiceTestCase):
    def setUp(self):
        super(ArtistServiceTest, self).setUp()

        self.data_producer.player().populate(self.data_facade)
        self.artist_repo = self.data_facade.artist_repo

    def test_delete_artist(self):
        name = "name"
        artist_id = IdentityService.id_artist(name)
        self.data_producer.artist(artist_id, name).video("source").populate(
            self.data_facade
        )

        artist = self.artist_repo.get(artist_id)
        self.evt_expecter.expect(Evt.ArtistDeleted, artist.id, artist.ids).from_(
            Cmd.DeleteArtist, artist.id
        )

        self.assertIsNone(self.artist_repo.get(artist_id))

    def test_create_artist(self):
        video_id = IdentityService.id_video("source")
        self.data_producer.video("source", artist="artist").populate(self.data_facade)

        artist_id = IdentityService.id_artist("artist")
        self.evt_expecter.expect(
            Evt.ArtistCreated, artist_id, "artist", [video_id], None
        ).from_event(
            VideoEvt.VideoCreated,
            video_id,
            "source",
            None,
            "album",
            "artist",
            "title",
            300,
            "http",
            "thumbnail",
            VideoState.CREATED,
        )

    def test_add_video_updates_artist(self):
        video_id_1 = IdentityService.id_video("source")
        video_id_2 = IdentityService.id_video("source2")
        artist_id = IdentityService.id_artist("artist")
        self.data_producer.video("source2", artist="artist").populate(self.data_facade)
        self.data_producer.artist(artist_id, "artist").video(
            "source", artist="artist"
        ).populate(self.data_facade)

        self.evt_expecter.expect(
            Evt.ArtistVideosUpdated, artist_id, [video_id_1, video_id_2]
        ).from_event(
            VideoEvt.VideoCreated,
            video_id_2,
            "source2",
            None,
            "album",
            "artist",
            "title",
            300,
            "http",
            "thumbnail",
            VideoState.CREATED,
        )

    def test_delete_video_updates_artist(self):
        artist_id = IdentityService.id_artist("artist")
        video_id_1 = IdentityService.id_video("source1")
        video_id_2 = IdentityService.id_video("source2")
        self.data_producer.artist(artist_id, "artist").video(
            "source1", artist="artist"
        ).video("source2", artist="artist").populate(self.data_facade)

        self.evt_expecter.expect(
            Evt.ArtistVideosUpdated, artist_id, [video_id_2]
        ).from_event(
            VideoEvt.VideoDeleted,
            video_id_1,
        )

    def test_delete_video_deletes_artist(self):
        artist_id = IdentityService.id_artist("artist")
        video_id = IdentityService.id_video("source")
        self.data_producer.artist(artist_id, "artist").video(
            "source", artist="artist"
        ).populate(self.data_facade)

        self.evt_expecter.expect(Evt.ArtistDeleted, artist_id, []).from_event(
            VideoEvt.VideoDeleted,
            video_id,
        )
