from OpenCast.app.command import playlist as Cmd
from OpenCast.domain.event import playlist as Evt
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class PlaylistServiceTest(ServiceTestCase):
    def setUp(self):
        super(PlaylistServiceTest, self).setUp()

        self.playlist_repo = self.data_facade.playlist_repo

    def test_create_playlist(self):
        name = "name"
        content = [IdentityService.id_video("source")]
        playlist_id = IdentityService.id_playlist()

        self.evt_expecter.expect(Evt.PlaylistCreated, playlist_id, name, content).from_(
            Cmd.CreatePlaylist, playlist_id, name, content
        )

    def test_delete_playlist(self):
        playlist_id = IdentityService.id_playlist()
        other_playlist_id = IdentityService.id_playlist()
        self.data_producer.playlist(playlist_id, "name", []).playlist(
            other_playlist_id, "other", []
        ).populate(self.data_facade)

        self.evt_expecter.expect(Evt.PlaylistDeleted, playlist_id).from_(
            Cmd.DeletePlaylist, playlist_id
        )

        self.assertListEqual(
            [self.playlist_repo.get(other_playlist_id)], self.playlist_repo.list()
        )

    def test_rename_playlist(self):
        playlist_id = IdentityService.id_playlist()
        self.data_producer.playlist(playlist_id, "name", []).populate(self.data_facade)

        new_name = "renamed"
        self.evt_expecter.expect(Evt.PlaylistRenamed, playlist_id, new_name).from_(
            Cmd.RenamePlaylist, playlist_id, new_name
        )

    def test_update_playlist_content(self):
        playlist_id = IdentityService.id_playlist()
        self.data_producer.playlist(playlist_id, "name", []).populate(self.data_facade)

        new_content = [IdentityService.id_video("source")]
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlist_id, new_content
        ).from_(Cmd.UpdatePlaylistContent, playlist_id, new_content)
