from test.shared.infra.data.facade_mock import DataFacadeMock
from test.shared.infra.facade_mock import InfraFacadeMock
from unittest.mock import Mock

from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.app.workflow.root import RootWorkflow
from OpenCast.app.workflow.video import VideoWorkflow
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService

from .util import WorkflowTestCase


class RootWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.video_repo = Mock()
        self.infra_facade = InfraFacadeMock()
        self.data_facade = DataFacadeMock()

        self.player_repo = self.data_facade.player_repo
        self.video_repo = self.data_facade.video_repo

        self.file_service = Mock()
        self.infra_facade.service_factory.make_file_service.return_value = (
            self.file_service
        )

        self.workflow = self.make_workflow(
            RootWorkflow, self.infra_facade, self.data_facade
        )

    def make_videos(self, count: int):
        return [
            Video(IdentityService.id_video(f"source_{i}"), f"source_{i}", None)
            for i in range(count)
        ]

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_creating_player(self):
        self.workflow.start()
        self.assertTrue(self.workflow.is_CREATING_PLAYER())

    def test_init_to_purging_videos(self):
        self.player_repo.exists.return_value = True
        self.video_repo.list.return_value = self.make_videos(3)

        self.workflow.start()
        self.assertTrue(self.workflow.is_PURGING_VIDEOS())

    def test_creating_player_to_aborted(self):
        self.workflow.to_CREATING_PLAYER()
        player_id = IdentityService.id_player()
        cmd = self.expect_dispatch(PlayerCmd.CreatePlayer, player_id)
        self.raise_error(cmd)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_creating_player_to_purging_videos(self):
        self.workflow.to_CREATING_PLAYER()
        self.video_repo.list.return_value = self.make_videos(3)
        player_id = IdentityService.id_player()
        cmd = self.expect_dispatch(PlayerCmd.CreatePlayer, player_id)
        self.raise_event(
            PlayerEvt.PlayerCreated,
            cmd.id,
            player_id,
            PlayerState.STOPPED,
            True,
            0,
            70,
        )
        self.assertTrue(self.workflow.is_PURGING_VIDEOS())

    def test_purging_videos_to_running_no_deletion(self):
        video = Mock()
        video.path.exists.return_value = True
        self.video_repo.list.return_value = [video]
        self.workflow.to_PURGING_VIDEOS()
        self.assertTrue(self.workflow.is_RUNNING())

    def test_purging_videos_to_running_with_deletion(self):
        video1 = Mock()
        video1.id = IdentityService.id_video("mock1")
        video1.path.exists.return_value = False

        video2 = Mock()
        video2.id = IdentityService.id_video("mock2")
        video2.path.exists.return_value = False

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
        self.assertTrue(self.workflow.is_RUNNING())

    def test_running_to_aborted(self):
        def raise_exception(*_):
            raise RuntimeError("server stopped")

        self.infra_facade.server.start.side_effect = raise_exception
        self.workflow.to_RUNNING()
        self.assertTrue(self.workflow.is_ABORTED())
