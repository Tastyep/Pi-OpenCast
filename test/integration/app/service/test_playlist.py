from OpenCast.app.command import playlist as Cmd
from OpenCast.config import settings
from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.event import playlist as Evt
from OpenCast.domain.model.playlist import Playlist
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class PlaylistServiceTest(ServiceTestCase):
    def setUp(self):
        super(PlaylistServiceTest, self).setUp()

        self.data_producer.player().populate(self.data_facade)
        self.playlist_repo = self.data_facade.playlist_repo

    def test_create_playlist(self):
        name = "name"
        content = [IdentityService.id_video("source")]
        playlist_id = IdentityService.id_playlist()
        generated = True

        self.evt_expecter.expect(
            Evt.PlaylistCreated, playlist_id, name, content, generated
        ).from_(Cmd.CreatePlaylist, playlist_id, name, content, generated)

    def test_delete_playlist(self):
        playlist_id = IdentityService.id_playlist()
        self.data_producer.select(Playlist, HOME_PLAYLIST.id).video("source").playlist(
            playlist_id, "name"
        ).video("source").video("other").playlist(
            IdentityService.id_playlist(), "other"
        ).populate(
            self.data_facade
        )

        playlist = self.playlist_repo.get(playlist_id)
        home_playlist = self.playlist_repo.get(HOME_PLAYLIST.id)
        self.evt_expecter.expect(
            Evt.PlaylistDeleted, playlist.id, playlist.name, playlist.ids
        ).expect(
            Evt.PlaylistContentUpdated,
            home_playlist.id,
            home_playlist.ids + [IdentityService.id_video("other")],
        ).from_(
            Cmd.DeletePlaylist, playlist.id
        )

        self.assertFalse(playlist in self.playlist_repo.list())

    def test_rename_playlist(self):
        playlist_id = IdentityService.id_playlist()
        self.data_producer.playlist(playlist_id, "name", []).populate(self.data_facade)

        playlist = self.playlist_repo.get(playlist_id)
        new_name = "renamed"
        self.evt_expecter.expect(Evt.PlaylistRenamed, playlist.id, new_name).from_(
            Cmd.RenamePlaylist, playlist.id, new_name
        )

    def test_queue_video(self):
        playlist_id = IdentityService.id_playlist()
        self.data_producer.video("source").playlist(playlist_id, "name", []).populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("source")
        playlist = self.playlist_repo.get(playlist_id)
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlist.id, [video_id]
        ).from_(
            Cmd.QueueVideo,
            playlist.id,
            video_id,
            queue_front=False,
        )

    def test_queue_video_above_max(self):
        playlist_id = IdentityService.id_playlist()
        video_ids = [
            IdentityService.id_video(f"source_{i}")
            for i in range(settings["player.queue.max_size"])
        ]
        self.data_producer.playlist(playlist_id, "name", video_ids).populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("above_max")
        playlist = self.playlist_repo.get(playlist_id)
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlist.id, video_ids[1:] + [video_id]
        ).from_(
            Cmd.QueueVideo,
            playlist.id,
            video_id,
            queue_front=False,
        )

    def test_queue_video_above_max_playing_video_first(self):
        playlist_id = IdentityService.id_playlist()
        video_ids = [
            IdentityService.id_video(f"source_{i}")
            for i in range(settings["player.queue.max_size"])
        ]
        self.data_producer.player().video(f"source_0").play(
            f"source_0"
        ).parent_producer().playlist(playlist_id, "name", video_ids).populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("above_max")
        playlist = self.playlist_repo.get(playlist_id)
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated,
            playlist.id,
            [video_ids[0]] + video_ids[2:] + [video_id],
        ).from_(
            Cmd.QueueVideo,
            playlist.id,
            video_id,
            queue_front=False,
        )

    def test_update_playlist_content(self):
        playlist_id = IdentityService.id_playlist()
        self.data_producer.playlist(playlist_id, "name", []).populate(self.data_facade)

        playlist = self.playlist_repo.get(playlist_id)
        new_content = [IdentityService.id_video("source")]
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlist.id, new_content
        ).from_(Cmd.UpdatePlaylistContent, playlist.id, new_content)

    def test_update_player_queue_content_above_max(self):
        playlist_id = HOME_PLAYLIST.id
        video_ids = [
            IdentityService.id_video(f"source_{i}")
            for i in range(settings["player.queue.max_size"])
        ]
        self.data_producer.player().parent_producer().select(
            Playlist, playlist_id
        ).set_ids(video_ids).populate(self.data_facade)

        new_content = video_ids + [IdentityService.id_video("above_max")]
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlist_id, new_content[1:]
        ).from_(Cmd.UpdatePlaylistContent, playlist_id, new_content)

    def test_update_player_queue_content_above_max_first_playing(self):
        playlist_id = HOME_PLAYLIST.id
        video_ids = [
            IdentityService.id_video(f"source_{i}")
            for i in range(settings["player.queue.max_size"])
        ]
        self.data_producer.player().video("source_0").play(
            "source_0"
        ).parent_producer().select(Playlist, playlist_id).set_ids(video_ids).populate(
            self.data_facade
        )

        new_content = video_ids + [IdentityService.id_video("above_max")]
        self.evt_expecter.expect(
            Evt.PlaylistContentUpdated, playlist_id, [new_content[0]] + new_content[2:]
        ).from_(Cmd.UpdatePlaylistContent, playlist_id, new_content)
