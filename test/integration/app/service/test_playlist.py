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
        self.data_producer.playlist("name").playlist("other").populate(self.data_facade)

        playlists = self.playlist_repo.list()
        self.evt_expecter.expect(Evt.PlaylistDeleted, playlists[0].id).from_(
            Cmd.DeletePlaylist, playlists[0].id
        )

        self.assertListEqual(
            [self.playlist_repo.get(playlists[1].id)], self.playlist_repo.list()
        )

    def test_rename_playlist(self):
        self.data_producer.playlist("name", []).populate(self.data_facade)

        playlists = self.playlist_repo.list()
        new_name = "renamed"
        self.evt_expecter.expect(Evt.PlaylistRenamed, playlists[0].id, new_name).from_(
            Cmd.RenamePlaylist, playlists[0].id, new_name
        )

    def test_queue_video(self):
        self.data_producer.video("source").playlist("name", []).populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("source")
        playlists = self.playlist_repo.list()
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlists[0].id, [video_id]
        ).from_(Cmd.QueueVideo, playlists[0].id, video_id, queue_front=False)

    def test_update_playlist_content(self):
        self.data_producer.playlist("name", []).populate(self.data_facade)

        playlists = self.playlist_repo.list()
        new_content = [IdentityService.id_video("source")]
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlists[0].id, new_content
        ).from_(Cmd.UpdatePlaylistContent, playlists[0].id, new_content)
