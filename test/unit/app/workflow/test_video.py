from unittest.mock import Mock

import OpenCast.app.command.video as Cmd
import OpenCast.domain.event.video as Evt
from OpenCast.app.service.error import OperationError
from OpenCast.app.workflow.video import Video, VideoWorkflow
from OpenCast.config import config
from OpenCast.domain.service.identity import IdentityService

from .util import WorkflowTestCase


class VideoWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super(VideoWorkflowTest, self).setUp()
        self.video_repo = Mock()
        self.video = Video(
            IdentityService.id_video("source"),
            "source",
            IdentityService.id_playlist("source"),
        )
        self.workflow = self.make_workflow(VideoWorkflow, self.video_repo, self.video)

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_completed(self):
        self.video_repo.exists.return_value = True
        self.workflow.start()
        self.video_repo.exists.assert_called_once_with(self.video.id)
        self.assertTrue(self.workflow.is_COMPLETED())

    def test_init_to_creating(self):
        self.video_repo.exists.return_value = False
        self.workflow.start()
        self.video_repo.exists.assert_called_once_with(self.video.id)
        self.assertTrue(self.workflow.is_CREATING())

    def test_creating_to_aborted(self):
        self.workflow.to_CREATING()
        cmd = self.expect_dispatch(Cmd.CreateVideo, *self.video.to_tuple())
        self.raise_error(self.workflow, cmd)
        self.assertTrue(self.workflow.is_ABORTED())

    def test_creating_to_identifying(self):
        self.workflow.to_CREATING()
        cmd = self.expect_dispatch(Cmd.CreateVideo, *self.video.to_tuple())
        self.raise_event(
            self.workflow,
            Evt.VideoCreated,
            cmd.id,
            *self.video.to_tuple(),
        )
        self.assertTrue(self.workflow.is_IDENTIFYING())

    def test_identifying_to_deleting(self):
        event = Evt.VideoCreated(None, *self.video.to_tuple())
        self.workflow.to_IDENTIFYING(event)
        cmd = self.expect_dispatch(Cmd.IdentifyVideo, self.video.id)
        self.raise_error(self.workflow, cmd)
        self.assertTrue(self.workflow.is_DELETING())

    def test_identifying_to_retrieving(self):
        event = Evt.VideoCreated(None, *self.video.to_tuple())
        self.workflow.to_IDENTIFYING(event)
        cmd = self.expect_dispatch(Cmd.IdentifyVideo, self.video.id)
        self.raise_event(
            self.workflow,
            Evt.VideoIdentified,
            cmd.id,
            self.video.id,
            "",
        )
        self.assertTrue(self.workflow.is_RETRIEVING())

    def test_retrieving_to_deleting(self):
        event = Evt.VideoIdentified(None, self.video.id, "")
        self.workflow.to_RETRIEVING(event)
        cmd = self.expect_dispatch(Cmd.RetrieveVideo, self.video.id, "/tmp")
        self.raise_error(self.workflow, cmd)
        self.assertTrue(self.workflow.is_DELETING())

    def test_retrieving_to_parsing(self):
        event = Evt.VideoIdentified(None, self.video.id, "")
        self.workflow.to_RETRIEVING(event)
        cmd = self.expect_dispatch(Cmd.RetrieveVideo, self.video.id, "/tmp")
        self.raise_event(
            self.workflow,
            Evt.VideoRetrieved,
            cmd.id,
            self.video.id,
            "/tmp/video.mp4",
        )
        self.assertTrue(self.workflow.is_PARSING())

    def test_parsing_to_deleting(self):
        event = Evt.VideoRetrieved(None, self.video.id, "/tmp")
        self.workflow.to_PARSING(event)
        cmd = self.expect_dispatch(Cmd.ParseVideo, self.video.id)
        self.raise_error(self.workflow, cmd)
        self.assertTrue(self.workflow.is_DELETING())

    def test_parsing_to_finalising(self):
        event = Evt.VideoRetrieved(None, self.video.id, "/tmp")
        self.workflow.to_PARSING(event)
        cmd = self.expect_dispatch(Cmd.ParseVideo, self.video.id)
        self.raise_event(
            self.workflow,
            Evt.VideoParsed,
            cmd.id,
            self.video.id,
            {},
        )
        self.assertTrue(self.workflow.is_FINALISING())

    def test_finalising_to_deleting(self):
        event = Evt.VideoParsed(None, self.video.id, {})
        self.workflow.to_FINALISING(event)
        cmd = self.expect_dispatch(
            Cmd.FetchVideoSubtitle, self.video.id, config["subtitle.language"]
        )
        self.raise_error(self.workflow, cmd)
        self.assertTrue(self.workflow.is_DELETING())

    def test_finalising_to_completed(self):
        event = Evt.VideoParsed(None, self.video.id, {})
        self.workflow.to_FINALISING(event)
        cmd = self.expect_dispatch(
            Cmd.FetchVideoSubtitle, self.video.id, config["subtitle.language"]
        )
        self.raise_event(
            self.workflow,
            Evt.VideoSubtitleFetched,
            cmd.id,
            self.video.id,
            "/tmp",
        )
        self.assertTrue(self.workflow.is_COMPLETED())

    def test_deleting_to_aborted(self):
        cmd = Cmd.IdentifyVideo(None, self.video.id)
        error = OperationError(cmd, "")
        self.workflow.to_DELETING(error)
        cmd = self.expect_dispatch(Cmd.DeleteVideo, self.video.id)
        self.raise_event(
            self.workflow,
            Evt.VideoDeleted,
            cmd.id,
            self.video.id,
        )
        self.assertTrue(self.workflow.is_ABORTED())
