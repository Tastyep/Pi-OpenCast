from OpenCast.app.command import album as Cmd
from OpenCast.domain.event import album as Evt
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class AlbumServiceTest(ServiceTestCase):
    def setUp(self):
        super(AlbumServiceTest, self).setUp()

        self.data_producer.player().populate(self.data_facade)
        self.album_repo = self.data_facade.album_repo

    def test_create_album(self):
        name = "name"
        album_id = IdentityService.id_album(name)
        ids = [IdentityService.id_video("source")]
        thumbnail = "thumbnail"

        self.evt_expecter.expect(
            Evt.AlbumCreated, album_id, name, ids, thumbnail
        ).from_(Cmd.CreateAlbum, album_id, name, ids, thumbnail)

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

    def test_update_album_videos(self):
        name = "name"
        album_id = IdentityService.id_album(name)
        self.data_producer.album(album_id, name, []).populate(self.data_facade)

        album = self.album_repo.get(album_id)
        ids = [IdentityService.id_video("source")]
        self.evt_expecter.expect(Evt.AlbumVideosUpdated, album.id, ids).from_(
            Cmd.UpdateAlbumVideos, album.id, ids
        )
