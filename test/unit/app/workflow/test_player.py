from unittest.mock import Mock

import OpenCast.app.command.player as PlayerCmd
import OpenCast.app.command.playlist as PlaylistCmd
import OpenCast.app.command.video as VideoCmd
import OpenCast.domain.event.player as PlayerEvt
import OpenCast.domain.event.playlist as PlaylistEvt
import OpenCast.domain.event.video as VideoEvt
from OpenCast.app.workflow.player import (
    QueuePlaylistWorkflow,
    QueueVideoWorkflow,
    StreamPlaylistWorkflow,
    StreamVideoWorkflow,
    Video,
    VideoWorkflow,
)
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.service.identity import IdentityService

from .util import WorkflowTestCase


class QueueVideoWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super(QueueVideoWorkflowTest, self).setUp()
        self.video_repo = self.data_facade.video_repo
        self.playlist_repo = self.data_facade.playlist_repo

        self.video_repo.exists.return_value = True

        self.player_playlist = Mock()
        self.player_playlist.ids = []
        self.playlist_repo.get.return_value = self.player_playlist

        self.player_id = IdentityService.id_player()
        self.player_playlist_id = IdentityService.id_playlist()

        player = Mock()
        player.queue = self.player_playlist_id
        self.data_facade.player_repo.get_player.return_value = player

        self.video = Video(
            IdentityService.id_video("source"),
            "source",
            collection_id=None,
        )
        self.workflow = self.make_workflow(
            QueueVideoWorkflow,
            self.video,
            self.player_playlist_id,
            queue_front=False,
        )

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_collecting(self):
        self.expect_workflow_creation(VideoWorkflow)
        self.workflow.start()
        self.assertTrue(self.workflow.is_COLLECTING())

    def test_collecting_to_aborted(self):
        (video_workflow,) = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()
        video_workflow_id = IdentityService.id_workflow(VideoWorkflow, self.video.id)
        self.raise_event(
            video_workflow.Aborted, video_workflow_id, video_workflow.video.id
        )
        self.assertTrue(self.workflow.is_ABORTED())

    def test_collecting_to_queueing_with_workflow_completed(self):
        (video_workflow,) = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()
        video_workflow_id = IdentityService.id_workflow(VideoWorkflow, self.video.id)
        self.raise_event(
            video_workflow.Completed, video_workflow_id, self.workflow.video.id
        )
        self.assertTrue(self.workflow.is_QUEUEING())

    def test_collecting_to_queueing_with_video_created(self):
        (video_workflow,) = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()

        cmd_id = IdentityService.id_command(VideoCmd.CreateVideo, self.video.id)
        self.raise_event(
            VideoEvt.VideoCreated,
            cmd_id,
            self.video.id,
            self.video.source,
            self.video.collection_id,
            "artist",
            "album",
            "title",
            300,
            "m3u8",
            "thumbnail",
            VideoState.CREATED,
        )
        self.assertTrue(self.workflow.is_QUEUEING())

    def test_collecting_to_removing(self):
        (video_workflow,) = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()
        self.player_playlist.ids = [self.video.id]
        video_workflow_id = IdentityService.id_workflow(VideoWorkflow, self.video.id)
        self.raise_event(
            video_workflow.Completed, video_workflow_id, self.workflow.video.id
        )
        self.assertTrue(self.workflow.is_REMOVING())

    def test_removing_to_queuing(self):
        event = VideoWorkflow.Completed(self.workflow.id, self.workflow.video.id)
        self.player_playlist.ids = [self.video.id]
        self.workflow.to_REMOVING(event)
        cmd = self.expect_dispatch(
            PlaylistCmd.UpdatePlaylistContent, self.player_playlist_id, []
        )
        self.raise_event(
            PlaylistEvt.PlaylistContentUpdated,
            cmd.id,
            self.player_playlist_id,
            ids=[],
        )
        self.assertTrue(self.workflow.is_QUEUEING())

    def test_queueing_to_aborted(self):
        event = VideoWorkflow.Completed(self.workflow.id, self.workflow.video.id)
        self.workflow.to_QUEUEING(event)
        cmd = self.expect_dispatch(
            PlaylistCmd.QueueVideo,
            self.player_playlist_id,
            self.video.id,
            queue_front=False,
        )
        self.raise_error(cmd)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_queueing_to_completed(self):
        event = VideoWorkflow.Completed(self.workflow.id, self.workflow.video.id)
        self.workflow.to_QUEUEING(event)
        cmd = self.expect_dispatch(
            PlaylistCmd.QueueVideo,
            self.player_playlist_id,
            self.video.id,
            queue_front=False,
        )
        self.raise_event(
            PlaylistEvt.PlaylistContentUpdated,
            cmd.id,
            self.player_playlist_id,
            [self.video.id],
        )
        self.assertTrue(self.workflow.is_COMPLETED())


class QueuePlaylistWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super(QueuePlaylistWorkflowTest, self).setUp()
        self.video_repo = self.data_facade.video_repo
        self.video_repo.exists.return_value = True
        self.player_playlist_id = IdentityService.id_playlist()

    def make_test_workflow(self, video_count=2):
        collection_id = IdentityService.random()
        sources = [f"src{i}" for i in range(video_count)]
        videos = [
            Video(IdentityService.id_video(source), source, collection_id)
            for source in sources
        ]
        return self.make_workflow(
            QueuePlaylistWorkflow, videos, self.player_playlist_id
        )

    def test_initial(self):
        workflow = self.make_test_workflow()
        self.assertTrue(workflow.is_INITIAL())

    def test_init_to_queueing(self):
        workflow = self.make_test_workflow()
        self.expect_workflow_creation(QueueVideoWorkflow)
        workflow.start()
        self.assertTrue(workflow.is_QUEUEING())

    def test_queueing_to_queueing_from_completed(self):
        workflow = self.make_test_workflow()
        video_id = workflow.videos[0].id
        queue_workflows = self.expect_workflow_creation(QueueVideoWorkflow, 2)
        workflow.to_QUEUEING(None)
        self.raise_event(queue_workflows[0].Completed, queue_workflows[0].id, video_id)
        self.assertTrue(workflow.is_QUEUEING())

    def test_queueing_to_queueing_from_aborted(self):
        workflow = self.make_test_workflow()
        video_id = workflow.videos[0].id
        queue_workflows = self.expect_workflow_creation(QueueVideoWorkflow, 2)
        workflow.to_QUEUEING(None)
        self.raise_event(queue_workflows[0].Aborted, queue_workflows[0].id, video_id)
        self.assertTrue(workflow.is_QUEUEING())

    def test_queueing_to_completed_from_completed(self):
        workflow = self.make_test_workflow(video_count=1)
        video_id = workflow.videos[0].id
        (queue_workflow,) = self.expect_workflow_creation(QueueVideoWorkflow)
        workflow.to_QUEUEING(None)
        self.raise_event(queue_workflow.Completed, queue_workflow.id, video_id)
        self.assertTrue(workflow.is_COMPLETED())

    def test_queueing_to_completed_from_aborted(self):
        workflow = self.make_test_workflow(video_count=1)
        video_id = workflow.videos[0].id
        (queue_workflow,) = self.expect_workflow_creation(QueueVideoWorkflow)
        workflow.to_QUEUEING(None)
        self.raise_event(queue_workflow.Aborted, queue_workflow.id, video_id)
        self.assertTrue(workflow.is_COMPLETED())


class StreamVideoWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super(StreamVideoWorkflowTest, self).setUp()
        self.video_repo = self.data_facade.video_repo
        self.video_repo.exists.return_value = True
        self.player_playlist_id = IdentityService.id_playlist()

        self.player_id = IdentityService.id_player()
        self.video = Video(
            IdentityService.id_video("source"),
            "source",
            collection_id=None,
        )
        self.workflow = self.make_workflow(
            StreamVideoWorkflow,
            self.video,
            self.player_playlist_id,
        )

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_queueing(self):
        self.expect_workflow_creation(QueueVideoWorkflow)
        self.workflow.start()
        self.assertTrue(self.workflow.is_QUEUEING())

    def test_queueing_to_aborted(self):
        (queue_workflow,) = self.expect_workflow_creation(QueueVideoWorkflow)
        self.workflow.to_QUEUEING()
        queue_workflow.start.assert_called_once()
        self.raise_event(
            queue_workflow.Aborted, queue_workflow.id, self.workflow.video.id
        )
        self.assertTrue(self.workflow.is_ABORTED())

    def test_queueing_to_synchronizing_with_queue_workflow_completed(self):
        (queue_workflow,) = self.expect_workflow_creation(QueueVideoWorkflow)
        self.workflow.to_QUEUEING()
        queue_workflow.start.assert_called_once()
        self.raise_event(
            queue_workflow.Completed, queue_workflow.id, self.workflow.video.id
        )
        self.assertTrue(self.workflow.is_SYNCHRONIZING())

    def test_queueing_to_synchronizing_with_video_workflow_completed(self):
        (queue_workflow,) = self.expect_workflow_creation(QueueVideoWorkflow)
        self.workflow.to_QUEUEING()
        queue_workflow.start.assert_called_once()
        video_workflow_id = IdentityService.id_workflow(VideoWorkflow, self.video.id)
        self.raise_event(VideoWorkflow.Completed, video_workflow_id, self.video.id)
        self.assertTrue(self.workflow.is_SYNCHRONIZING())

    def test_starting_to_aborted(self):
        event = QueueVideoWorkflow.Completed(self.workflow.id, self.workflow.video.id)
        self.workflow.to_STARTING(event)
        cmd = self.expect_dispatch(
            PlayerCmd.PlayVideo, self.player_id, self.video.id, self.player_playlist_id
        )
        self.raise_error(cmd)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_queueing_to_completed(self):
        event = QueueVideoWorkflow.Completed(self.workflow.id, self.workflow.video.id)
        self.workflow.to_STARTING(event)
        cmd = self.expect_dispatch(
            PlayerCmd.PlayVideo, self.player_id, self.video.id, self.player_playlist_id
        )
        self.raise_event(
            PlayerEvt.PlayerStateUpdated,
            cmd.id,
            self.player_id,
            PlayerState.STOPPED,
            PlayerState.PLAYING,
            self.video.id,
        )
        self.assertTrue(self.workflow.is_COMPLETED())


class StreamPlaylistWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super(StreamPlaylistWorkflowTest, self).setUp()
        self.video_repo = self.data_facade.video_repo
        self.video_repo.exists.return_value = True
        self.player_playlist_id = IdentityService.id_playlist()

    def make_test_workflow(self, video_count=2):
        collection_id = IdentityService.random()
        sources = [f"src{i}" for i in range(video_count)]
        videos = [
            Video(IdentityService.id_video(source), source, collection_id)
            for source in sources
        ]
        return self.make_workflow(
            StreamPlaylistWorkflow, videos, self.player_playlist_id
        )

    def test_initial(self):
        workflow = self.make_test_workflow()
        self.assertTrue(workflow.is_INITIAL())

    def test_init_to_starting(self):
        workflow = self.make_test_workflow()
        self.expect_workflow_creation(StreamVideoWorkflow)
        workflow.start()
        self.assertTrue(workflow.is_STARTING())

    def test_starting_to_queueing_from_completed(self):
        workflow = self.make_test_workflow()
        video_id = workflow.videos[0].id
        (play_workflow,) = self.expect_workflow_creation(StreamVideoWorkflow)
        workflow.to_STARTING(None)

        self.expect_workflow_creation(QueueVideoWorkflow)
        self.raise_event(play_workflow.Completed, play_workflow.id, video_id)
        self.assertTrue(workflow.is_QUEUEING())

    def test_starting_to_starting_from_aborted(self):
        workflow = self.make_test_workflow()
        video_id = workflow.videos[0].id
        play_workflows = self.expect_workflow_creation(StreamVideoWorkflow, 2)
        workflow.to_STARTING(None)
        self.raise_event(play_workflows[0].Aborted, play_workflows[0].id, video_id)
        self.assertTrue(workflow.is_STARTING())

    def test_starting_to_completed_from_completed(self):
        workflow = self.make_test_workflow(video_count=1)
        video_id = workflow.videos[0].id
        (play_workflow,) = self.expect_workflow_creation(StreamVideoWorkflow)
        workflow.to_STARTING(None)
        self.raise_event(play_workflow.Completed, play_workflow.id, video_id)
        self.assertTrue(workflow.is_COMPLETED())

    def test_starting_to_completed_from_aborted(self):
        workflow = self.make_test_workflow(video_count=1)
        video_id = workflow.videos[0].id
        (play_workflow,) = self.expect_workflow_creation(StreamVideoWorkflow)
        workflow.to_STARTING(None)
        self.raise_event(play_workflow.Aborted, play_workflow.id, video_id)
        self.assertTrue(workflow.is_COMPLETED())

    def test_queueing_to_queueing_from_completed(self):
        workflow = self.make_test_workflow(video_count=3)
        queue_workflows = self.expect_workflow_creation(QueueVideoWorkflow, 2)
        streamed_video = workflow.videos.pop()
        queueing_video = workflow.videos[-1]
        workflow.to_QUEUEING(
            StreamVideoWorkflow.Completed(workflow.id, streamed_video.id)
        )
        self.raise_event(
            queue_workflows[0].Completed, queue_workflows[0].id, queueing_video.id
        )
        self.assertTrue(workflow.is_QUEUEING())

    def test_queueing_to_queueing_from_aborted(self):
        workflow = self.make_test_workflow(video_count=3)
        queue_workflows = self.expect_workflow_creation(QueueVideoWorkflow, 2)
        streamed_video = workflow.videos.pop()
        queueing_video = workflow.videos[-1]
        workflow.to_QUEUEING(
            StreamVideoWorkflow.Completed(workflow.id, streamed_video.id)
        )
        self.raise_event(
            queue_workflows[0].Aborted, queue_workflows[0].id, queueing_video.id
        )
        self.assertTrue(workflow.is_QUEUEING())

    def test_queueing_to_completed_from_completed(self):
        workflow = self.make_test_workflow(video_count=2)
        (queue_workflow,) = self.expect_workflow_creation(QueueVideoWorkflow)
        streamed_video = workflow.videos.pop()
        queueing_video = workflow.videos[-1]
        workflow.to_QUEUEING(
            StreamVideoWorkflow.Completed(workflow.id, streamed_video.id)
        )
        self.raise_event(queue_workflow.Completed, queue_workflow.id, queueing_video.id)
        self.assertTrue(workflow.is_COMPLETED())

    def test_queueing_to_completed_from_aborted(self):
        workflow = self.make_test_workflow(video_count=2)
        (queue_workflow,) = self.expect_workflow_creation(QueueVideoWorkflow)
        streamed_video = workflow.videos.pop()
        queueing_video = workflow.videos[-1]
        workflow.to_QUEUEING(
            StreamVideoWorkflow.Completed(workflow.id, streamed_video.id)
        )
        self.raise_event(queue_workflow.Aborted, queue_workflow.id, queueing_video.id)
        self.assertTrue(workflow.is_COMPLETED())
