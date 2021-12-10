from test.unit.domain.model.util import ModelTestCase

from OpenCast.domain.error import DomainError
from OpenCast.domain.event import artist as Evt
from OpenCast.domain.model.artist import Artist
from OpenCast.domain.service.identity import IdentityService


class ArtistTest(ModelTestCase):
    def setUp(self):
        name = "name"
        self.artist = Artist(IdentityService.id_artist(name), name, [], "thumbnail")
        self.artist.release_events()

    def test_construction(self):
        name = "name"
        ids = [IdentityService.random()]
        thumbnail = "thumbnail"
        id = IdentityService.id_artist(name)
        artist = Artist(id, name, ids, thumbnail)
        self.expect_events(artist, Evt.ArtistCreated)

    def test_empty(self):
        self.assertTrue(self.artist.empty())
        self.artist = Artist(
            IdentityService.id_artist("name"),
            "name",
            [IdentityService.random()],
            "thumbnail",
        )
        self.assertFalse(self.artist.empty())

    def test_delete(self):
        self.artist.delete()
        self.expect_events(self.artist, Evt.ArtistDeleted)

    def test_set_thumbnail(self):
        self.artist.thumbnail = "new_value"
        self.expect_events(self.artist, Evt.ArtistThumbnailUpdated)

    def test_add(self):
        first = IdentityService.random()
        self.artist.add(first)
        self.assertListEqual([first], self.artist.ids)

        second = IdentityService.random()
        self.artist.add(second)
        self.assertListEqual([first, second], self.artist.ids)

        self.expect_events(
            self.artist, Evt.ArtistVideosUpdated, Evt.ArtistVideosUpdated
        )

    def test_add_already_contained(self):
        video_id = IdentityService.random()
        self.artist.add(video_id)
        with self.assertRaises(DomainError) as ctx:
            self.artist.add(video_id)
        self.assertEqual("video already registered", str(ctx.exception))

    def test_remove(self):
        self.artist.add(IdentityService.id_video("source1"))
        self.artist.add(IdentityService.id_video("source2"))
        self.artist.release_events()
        self.artist.remove(IdentityService.id_video("source1"))
        self.expect_events(self.artist, Evt.ArtistVideosUpdated)

    def test_remove_unknown(self):
        video_id = IdentityService.id_video("source1")
        with self.assertRaises(DomainError) as ctx:
            self.artist.remove(video_id)
        self.assertEqual(
            "video not from artist",
            str(ctx.exception),
        )
