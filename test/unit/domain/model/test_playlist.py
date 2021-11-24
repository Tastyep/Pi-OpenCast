import OpenCast.domain.event.playlist as Evt
from OpenCast.domain.error import DomainError
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
        self.assertEqual(False, playlist.generated)
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

    def test_remove_unknown(self):
        video_id = IdentityService.id_video("source1")
        with self.assertRaises(DomainError) as ctx:
            self.playlist.remove(video_id)
        self.assertEqual(
            "video not in playlist",
            str(ctx.exception),
        )

    def test_delete(self):
        self.playlist.delete()
        self.expect_events(self.playlist, Evt.PlaylistDeleted)

    def test_delete_generated(self):
        playlist = Playlist(None, "name", [], True)
        with self.assertRaises(DomainError) as ctx:
            playlist.delete()
        self.assertEqual("cannot delete generated playlists", str(ctx.exception))
