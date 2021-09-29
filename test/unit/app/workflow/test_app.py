from unittest.mock import Mock, patch

from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.command import playlist as PlaylistCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.app.workflow.app import InitWorkflow
from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService

from .util import WorkflowTestCase


class InitWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.video_repo = Mock()

        self.player_repo = self.data_facade.player_repo
        self.video_repo = self.data_facade.video_repo

        self.workflow = self.make_workflow(InitWorkflow)

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_creating_player(self):
        self.workflow.start()
        self.assertTrue(self.workflow.is_CREATING_PLAYER())

    def test_init_to_purging_videos(self):
        self.player_repo.exists.return_value = True

        video = Video(IdentityService.id_video("source"), "source", location="unknown")
        self.video_repo.list.return_value = [video]

        self.workflow.start()
        self.assertTrue(self.workflow.is_PURGING_VIDEOS())

    @patch("OpenCast.app.workflow.app.IdentityService")
    def test_creating_player_to_aborted(self, identityMock):
        player_id = IdentityService.id_player()
        identityMock.id_player.return_value = player_id

        self.workflow.to_CREATING_PLAYER()
        createPlaylistId = IdentityService.id_command(
            PlaylistCmd.CreatePlaylist, HOME_PLAYLIST.id
        )
        createPlayerId = IdentityService.id_command(PlayerCmd.CreatePlayer, player_id)
        expected_cmds = [
            PlaylistCmd.CreatePlaylist(
                createPlaylistId,
                HOME_PLAYLIST.id,
                HOME_PLAYLIST.name,
                [],
                True,
            ),
            PlayerCmd.CreatePlayer(createPlayerId, player_id, HOME_PLAYLIST.id),
        ]
        self.expect_dispatch_l(expected_cmds)
        self.raise_error(expected_cmds[-1])
        self.assertTrue(self.workflow.is_ABORTED())

    @patch("OpenCast.app.workflow.app.IdentityService")
    def test_creating_player_to_purging_videos(self, identityMock):
        player_id = IdentityService.id_player()
        identityMock.id_player.return_value = player_id
        video = Video(IdentityService.id_video("source"), "source", location="unknown")
        self.video_repo.list.return_value = [video]

        self.workflow.to_CREATING_PLAYER()
        createPlaylistId = IdentityService.id_command(
            PlaylistCmd.CreatePlaylist, HOME_PLAYLIST.id
        )
        createPlayerId = IdentityService.id_command(PlayerCmd.CreatePlayer, player_id)
        expected_cmds = [
            PlaylistCmd.CreatePlaylist(
                createPlaylistId, HOME_PLAYLIST.id, HOME_PLAYLIST.name, [], True
            ),
            PlayerCmd.CreatePlayer(createPlayerId, player_id, HOME_PLAYLIST.id),
        ]
        self.expect_dispatch_l(expected_cmds)
        self.raise_event(
            PlayerEvt.PlayerCreated,
            createPlayerId,
            player_id,
            HOME_PLAYLIST.id,
            PlayerState.STOPPED,
            True,
            0,
            70,
        )
        self.assertTrue(self.workflow.is_PURGING_VIDEOS())

    @patch("OpenCast.app.workflow.app.Path")
    def test_purging_videos_to_completed_no_deletion_because_on_disk(
        self, path_cls_mock
    ):
        path_inst = path_cls_mock.return_value
        path_inst.exists.return_value = True

        video = Mock()
        video.streamable.return_value = False

        self.video_repo.list.return_value = [video]
        self.workflow.to_PURGING_VIDEOS()
        self.assertTrue(self.workflow.is_COMPLETED())

    @patch("OpenCast.app.workflow.app.Path")
    def test_purging_videos_to_completed_no_deletion_because_streamable(
        self, path_cls_mock
    ):
        path_inst = path_cls_mock.return_value
        path_inst.exists.return_value = False

        video = Mock()
        video.streamable.return_value = True

        self.video_repo.list.return_value = [video]
        self.workflow.to_PURGING_VIDEOS()
        self.assertTrue(self.workflow.is_COMPLETED())

    @patch("OpenCast.app.workflow.app.Path")
    def test_purging_videos_to_completed_with_deletion(self, path_cls_mock):
        path_inst = path_cls_mock.return_value
        path_inst.exists.return_value = False

        video1 = Mock()
        video1.id = IdentityService.id_video("mock1")
        video1.streamable.return_value = False

        video2 = Mock()
        video2.id = IdentityService.id_video("mock2")
        video2.location = None

        self.video_repo.list.return_value = [video1, video2]
        self.workflow.to_PURGING_VIDEOS()

        cmd = self.expect_dispatch(VideoCmd.DeleteVideo, video2.id)
        self.raise_event(
            VideoEvt.VideoDeleted,
            cmd.id,
            video2.id,
        )

        self.assertTrue(self.workflow.is_PURGING_VIDEOS())
        cmd = self.expect_dispatch(VideoCmd.DeleteVideo, video1.id)
        self.raise_event(
            VideoEvt.VideoDeleted,
            cmd.id,
            video1.id,
        )
        self.assertTrue(self.workflow.is_COMPLETED())
