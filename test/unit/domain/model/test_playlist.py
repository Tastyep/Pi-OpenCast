import OpenCast.domain.event.playlist as Evt
from OpenCast.domain.model.playlist import Playlist
from OpenCast.domain.service.identity import IdentityService

from .util import ModelTestCase


class PlaylistTest(ModelTestCase):
    def setUp(self):
        self.playlist = Playlist(IdentityService.id_playlist(), "name", [])
        self.playlist.release_events()

    def test_construction(self):
        content = [IdentityService.id_video("")]
        playlist = Playlist(None, "name", content)
        self.assertEqual("name", playlist.name)
        self.assertEqual(content, playlist.ids)
        self.expect_events(playlist, Evt.PlaylistCreated)

    def test_rename(self):
        self.playlist.name = "renamed"
        self.expect_events(self.playlist, Evt.PlaylistRenamed)

    def test_update_content(self):
        self.playlist.ids = [IdentityService.id_video("source")]
        self.expect_events(self.playlist, Evt.PlaylistContentUpdated)

    def test_remove(self):
        self.playlist.ids = [
            IdentityService.id_video("source1"),
            IdentityService.id_video("source2"),
        ]
        self.playlist.release_events()
        self.playlist.remove(IdentityService.id_video("source1"))
        self.expect_events(self.playlist, Evt.PlaylistContentUpdated)

    def test_delete(self):
        self.playlist.delete()
        self.expect_events(self.playlist, Evt.PlaylistDeleted)
