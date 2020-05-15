from unittest.mock import Mock

import OpenCast.app.command.player as Cmd
import OpenCast.domain.event.player as Evt
from OpenCast.app.workflow.player import (
    QueueVideoWorkflow,
    StreamVideoWorkflow,
    Video,
    VideoWorkflow,
)
from OpenCast.domain.service.identity import IdentityService

from .util import WorkflowTestCase


class QueueVideoWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super(QueueVideoWorkflowTest, self).setUp()
        self.video_repo = Mock()
        self.video_repo.exists.return_value = True

        self.player_id = IdentityService.id_player()
        self.video = Video(
            IdentityService.id_video("source"),
            "source",
            IdentityService.id_playlist("source"),
        )
        self.workflow = self.make_workflow(
            QueueVideoWorkflow, self.video_repo, self.video,
        )

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_collecting(self):
        self.expect_workflow_creation(VideoWorkflow)
        self.workflow.start()
        self.assertTrue(self.workflow.is_COLLECTING())

    def test_collecting_to_aborted(self):
        video_workflow = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()
        self.raise_event(self.workflow, video_workflow.Aborted, video_workflow.id)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_collecting_to_queueing(self):
        video_workflow = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()
        self.raise_event(self.workflow, video_workflow.Completed, video_workflow.id)
        self.assertTrue(self.workflow.is_QUEUEING())

    def test_queueing_to_aborted(self):
        event = VideoWorkflow.Completed(self.workflow.id)
        self.workflow.to_QUEUEING(event)
        cmd = self.expect_dispatch(Cmd.QueueVideo, self.player_id, self.video.id)
        self.raise_error(self.workflow, cmd)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_queueing_to_completed(self):
        event = VideoWorkflow.Completed(self.workflow.id)
        self.workflow.to_QUEUEING(event)
        cmd = self.expect_dispatch(Cmd.QueueVideo, self.player_id, self.video.id)
        self.raise_event(
            self.workflow, Evt.VideoQueued, cmd.id, self.player_id, self.video.id,
        )
        self.assertTrue(self.workflow.is_COMPLETED())


class StreamVideoWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super(StreamVideoWorkflowTest, self).setUp()
        self.video_repo = Mock()
        self.video_repo.exists.return_value = True

        self.player_id = IdentityService.id_player()
        self.video = Video(
            IdentityService.id_video("source"),
            "source",
            IdentityService.id_playlist("source"),
        )
        self.workflow = self.make_workflow(
            StreamVideoWorkflow, self.video_repo, self.video,
        )

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_collecting(self):
        self.expect_workflow_creation(VideoWorkflow)
        self.workflow.start()
        self.assertTrue(self.workflow.is_COLLECTING())

    def test_collecting_to_aborted(self):
        video_workflow = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()
        self.raise_event(self.workflow, video_workflow.Aborted, video_workflow.id)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_collecting_to_starting(self):
        video_workflow = self.expect_workflow_creation(VideoWorkflow)
        self.workflow.to_COLLECTING()
        video_workflow.start.assert_called_once()
        self.raise_event(self.workflow, video_workflow.Completed, video_workflow.id)
        self.assertTrue(self.workflow.is_STARTING())

    def test_starting_to_aborted(self):
        event = VideoWorkflow.Completed(self.workflow.id)
        self.workflow.to_STARTING(event)
        cmd = self.expect_dispatch(Cmd.PlayVideo, self.player_id, self.video.id)
        self.raise_error(self.workflow, cmd)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_queueing_to_completed(self):
        event = VideoWorkflow.Completed(self.workflow.id)
        self.workflow.to_STARTING(event)
        cmd = self.expect_dispatch(Cmd.PlayVideo, self.player_id, self.video.id)
        self.raise_event(
            self.workflow, Evt.PlayerStarted, cmd.id, self.player_id, self.video.id,
        )
        self.assertTrue(self.workflow.is_COMPLETED())
