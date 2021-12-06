from test.unit.domain.model.util import ModelTestCase

from OpenCast.domain.error import DomainError
from OpenCast.domain.event import album as Evt
from OpenCast.domain.model.album import Album
from OpenCast.domain.service.identity import IdentityService


class AlbumTest(ModelTestCase):
    def setUp(self):
        name = "name"
        self.album = Album(IdentityService.id_album(name), name, [], "thumbnail")
        self.album.release_events()

    def test_construction(self):
        name = "name"
        ids = [IdentityService.random()]
        thumbnail = "thumbnail"
        id = IdentityService.id_album(name)
        album = Album(id, name, ids, thumbnail)
        self.expect_events(album, Evt.AlbumCreated)

    def test_delete(self):
        self.album.delete()
        self.expect_events(self.album, Evt.AlbumDeleted)

    def test_remove(self):
        self.album.ids = [
            IdentityService.id_video("source1"),
            IdentityService.id_video("source2"),
        ]
        self.album.release_events()
        self.album.remove(IdentityService.id_video("source1"))
        self.expect_events(self.album, Evt.AlbumVideosUpdated)

    def test_remove_unknown(self):
        video_id = IdentityService.id_video("source1")
        with self.assertRaises(DomainError) as ctx:
            self.album.remove(video_id)
        self.assertEqual(
            "video not in album",
            str(ctx.exception),
        )
