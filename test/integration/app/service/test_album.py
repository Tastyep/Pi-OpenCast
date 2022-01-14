from OpenCast.app.command import album as Cmd
from OpenCast.domain.event import album as Evt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class AlbumServiceTest(ServiceTestCase):
    def setUp(self):
        super(AlbumServiceTest, self).setUp()

        self.data_producer.player().populate(self.data_facade)
        self.album_repo = self.data_facade.album_repo

    def test_delete_album(self):
        name = "name"
        album_id = IdentityService.id_album(name)
        self.data_producer.album(album_id, name).video("source").populate(
            self.data_facade
        )

        album = self.album_repo.get(album_id)
        self.evt_expecter.expect(Evt.AlbumDeleted, album.id, album.ids).from_(
            Cmd.DeleteAlbum, album.id
        )

        self.assertIsNone(self.album_repo.get(album_id))

    def test_create_album(self):
        video_id = IdentityService.id_video("source")
        album_id = IdentityService.id_album("album")
        self.data_producer.video("source", album_id=album_id).populate(self.data_facade)

        metadata = {
            "title": "title",
            "duration": 300,
            "source_protocol": "http",
            "artist": "artist",
            "album": "album",
            "thumbnail": "thumbnail_url",
        }
        self.downloader.download_metadata.return_value = metadata

        deezer_data = [{"album": {"cover_medium": "cover_url"}}]
        self.deezer.search.return_value = deezer_data

        self.evt_expecter.expect(
            Evt.AlbumCreated, album_id, "album", [video_id], "cover_url"
        ).from_event(
            VideoEvt.VideoCreated,
            video_id,
            "source",
            None,
            None,
            album_id,
            "title",
            300,
            "http",
            "thumbnail_url",
            VideoState.CREATED,
        )

    def test_create_album_no_deezer_data(self):
        video_id = IdentityService.id_video("source")
        album_id = IdentityService.id_album("album")
        self.data_producer.video("source", album_id=album_id).populate(self.data_facade)

        metadata = {
            "title": "title",
            "duration": 300,
            "source_protocol": "http",
            "artist": "artist",
            "album": "album",
            "thumbnail": "thumbnail_url",
        }
        self.downloader.download_metadata.return_value = metadata

        self.deezer.search.return_value = []

        self.evt_expecter.expect(
            Evt.AlbumCreated, album_id, "album", [video_id], "thumbnail_url"
        ).from_event(
            VideoEvt.VideoCreated,
            video_id,
            "source",
            None,
            None,
            album_id,
            "title",
            300,
            "http",
            "thumbnail_url",
            VideoState.CREATED,
        )

    def test_add_video_updates_album(self):
        video_id_1 = IdentityService.id_video("source")
        video_id_2 = IdentityService.id_video("source2")
        album_id = IdentityService.id_album("album")
        self.data_producer.video("source2", album_id=album_id).populate(
            self.data_facade
        )
        self.data_producer.album(album_id, "album").video(
            "source", album_id=album_id
        ).populate(self.data_facade)

        self.evt_expecter.expect(
            Evt.AlbumVideosUpdated, album_id, [video_id_1, video_id_2]
        ).from_event(
            VideoEvt.VideoCreated,
            video_id_2,
            "source2",
            None,
            None,
            album_id,
            "title",
            300,
            "http",
            "thumbnail",
            VideoState.CREATED,
        )

    def test_delete_video_updates_album(self):
        album_id = IdentityService.id_album("album")
        video_id_1 = IdentityService.id_video("source1")
        video_id_2 = IdentityService.id_video("source2")
        self.data_producer.album(album_id, "album").video(
            "source1", album_id=album_id
        ).video("source2", album_id=album_id).populate(self.data_facade)

        self.evt_expecter.expect(
            Evt.AlbumVideosUpdated, album_id, [video_id_2]
        ).from_event(
            VideoEvt.VideoDeleted,
            video_id_1,
        )

    def test_delete_video_deletes_album(self):
        album_id = IdentityService.id_album("album")
        video_id = IdentityService.id_video("source")
        self.data_producer.album(album_id, "album").video(
            "source", album_id=album_id
        ).populate(self.data_facade)

        self.evt_expecter.expect(Evt.AlbumDeleted, album_id, []).from_event(
            VideoEvt.VideoDeleted,
            video_id,
        )
