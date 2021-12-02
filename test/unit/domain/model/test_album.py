from test.unit.domain.model.util import ModelTestCase

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
