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

    def test_empty(self):
        self.assertTrue(self.album.empty())
        self.album = Album(
            IdentityService.id_album("name"),
            "name",
            [IdentityService.random()],
            "thumbnail",
        )
        self.assertFalse(self.album.empty())

    def test_delete(self):
        self.album.delete()
        self.expect_events(self.album, Evt.AlbumDeleted)

    def test_add(self):
        first = IdentityService.random()
        self.album.add(first)
        self.assertListEqual([first], self.album.ids)

        second = IdentityService.random()
        self.album.add(second)
        self.assertListEqual([first, second], self.album.ids)

        self.expect_events(self.album, Evt.AlbumVideosUpdated, Evt.AlbumVideosUpdated)

    def test_add_already_contained(self):
        video_id = IdentityService.random()
        self.album.add(video_id)
        with self.assertRaises(DomainError) as ctx:
            self.album.add(video_id)
        self.assertEqual("video already in album", str(ctx.exception))

    def test_remove(self):
        self.album.add(IdentityService.id_video("source1"))
        self.album.add(IdentityService.id_video("source2"))
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
