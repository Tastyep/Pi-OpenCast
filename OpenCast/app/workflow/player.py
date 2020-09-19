""" Workflows running player related operations """

from collections import namedtuple
from enum import Enum, auto
from typing import List

import structlog

from OpenCast.app.command import player as PlayerCmd
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.service.identity import IdentityService

from .video import Video, VideoWorkflow
from .workflow import Workflow


class QueueVideoWorkflow(Workflow):
    Completed = namedtuple("QueueVideoWorkflowCompleted", ("id"))
    Aborted = namedtuple("QueueVideoWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        COLLECTING = auto()
        QUEUEING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["start",                     States.INITIAL,    States.COLLECTING],
        ["_video_workflow_completed", States.COLLECTING, States.QUEUEING],
        ["_video_workflow_aborted",   States.COLLECTING, States.ABORTED],
        ["_video_queued",             States.QUEUEING,   States.COMPLETED],
        ["_operation_error",          States.QUEUEING,   States.ABORTED],
    ]
    # fmt: on

    def __init__(self, id, app_facade, video_repo, video: Video, queue_front):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=QueueVideoWorkflow.States.INITIAL,
        )
        self._video_repo = video_repo
        self._video = video
        self._queue_front = queue_front

    # States
    def on_enter_COLLECTING(self):
        workflow_id = IdentityService.id_workflow(VideoWorkflow, self._video.id)
        workflow = self._factory.make_video_workflow(
            workflow_id, self._app_facade, self._video_repo, self._video
        )
        self._observe_start(workflow)

    def on_enter_QUEUEING(self, evt):
        self._observe_dispatch(
            PlayerEvt.VideoQueued,
            PlayerCmd.QueueVideo,
            IdentityService.id_player(),
            self._video.id,
            self._queue_front,
        )

    def on_enter_COMPLETED(self, _):
        self.complete()

    def on_enter_ABORTED(self, _):
        self.cancel()


class QueuePlaylistWorkflow(Workflow):
    Completed = namedtuple("QueuePlaylistWorkflowCompleted", ("id"))
    Aborted = namedtuple("QueuePlaylistWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        QUEUEING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_queue_videos",                      States.INITIAL,    States.QUEUEING],
        ["_queue_video_workflow_completed",    States.QUEUEING,   States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_completed",    States.QUEUEING,   "="],
        ["_queue_video_workflow_aborted",      States.QUEUEING,   States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_aborted",      States.QUEUEING,   "="],
    ]
    # fmt: on

    def __init__(
        self,
        id,
        app_facade,
        video_repo,
        videos: List[Video],
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=StreamVideoWorkflow.States.INITIAL,
        )
        self._video_repo = video_repo
        self._videos = videos[::-1]

    def start(
        self,
    ):
        self._queue_videos(None)

    # States
    def on_enter_QUEUEING(self, _):
        video = self._videos.pop()
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, video.id)
        workflow = self._factory.make_queue_video_workflow(
            workflow_id, self._app_facade, self._video_repo, video, queue_front=False
        )
        self._observe_start(workflow)

    def on_enter_COMPLETED(self, _):
        self.complete()

    def on_enter_ABORTED(self, _):
        self.cancel()

    # Conditions
    def _is_last_video(self, evt):
        return len(self._videos) == 0


class StreamVideoWorkflow(Workflow):
    Completed = namedtuple("StreamVideoWorkflowCompleted", ("id"))
    Aborted = namedtuple("StreamVideoWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        QUEUEING = auto()
        STARTING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["start",                           States.INITIAL,    States.QUEUEING],
        ["_queue_video_workflow_completed", States.QUEUEING,   States.STARTING],
        ["_queue_video_workflow_aborted",   States.QUEUEING,   States.ABORTED],
        ["_player_started",                 States.STARTING,   States.COMPLETED],
        ["_operation_error",                States.STARTING,   States.ABORTED],
    ]
    # fmt: on

    def __init__(self, id, app_facade, video_repo, video: Video):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=StreamVideoWorkflow.States.INITIAL,
        )

        self._video_repo = video_repo
        self._video = video

    # States
    def on_enter_QUEUEING(self):
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, self._video.id)
        workflow = self._factory.make_queue_video_workflow(
            workflow_id,
            self._app_facade,
            self._video_repo,
            self._video,
            queue_front=False,
        )
        self._observe_start(workflow)

    def on_enter_STARTING(self, evt):
        self._observe_dispatch(
            PlayerEvt.PlayerStarted,
            PlayerCmd.PlayVideo,
            IdentityService.id_player(),
            self._video.id,
        )

    def on_enter_COMPLETED(self, _):
        self.complete()

    def on_enter_ABORTED(self, _):
        self.cancel()


class StreamPlaylistWorkflow(Workflow):
    Completed = namedtuple("StreamPlaylistWorkflowCompleted", ("id"))
    Aborted = namedtuple("StreamPlaylistWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        STARTING = auto()
        QUEUEING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_play_video",                      States.INITIAL,  States.STARTING],
        ["_stream_video_workflow_completed", States.STARTING, States.COMPLETED, "_is_last_video"],   # noqa: E501
        ["_stream_video_workflow_completed", States.STARTING, States.QUEUEING],
        ["_stream_video_workflow_aborted",   States.STARTING, States.COMPLETED, "_is_last_video"],   # noqa: E501
        ["_stream_video_workflow_aborted",   States.STARTING, "="],

        ["_queue_video_workflow_completed",  States.QUEUEING, States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_completed",  States.QUEUEING, "="],
        ["_queue_video_workflow_aborted",    States.QUEUEING, States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_aborted",    States.QUEUEING, "="],
    ]
    # fmt: on

    def __init__(
        self,
        id,
        app_facade,
        video_repo,
        videos: List[Video],
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=StreamVideoWorkflow.States.INITIAL,
        )

        self._video_repo = video_repo
        self._videos = videos[::-1]

    def start(self):
        self._play_video(None)

    # States
    def on_enter_STARTING(self, _):
        video = self._videos.pop()
        workflow_id = IdentityService.id_workflow(StreamVideoWorkflow, video.id)
        workflow = self._factory.make_stream_video_workflow(
            workflow_id, self._app_facade, self._video_repo, video
        )
        self._observe_start(
            workflow,
        )

    def on_enter_QUEUEING(self, _):
        video = self._videos.pop()
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, video.id)
        workflow = self._factory.make_queue_video_workflow(
            workflow_id, self._app_facade, self._video_repo, video, queue_front=True
        )
        self._observe_start(
            workflow,
        )

    def on_enter_COMPLETED(self, _):
        self.complete()

    def on_enter_ABORTED(self, _):
        self.cancel()

    # Conditions
    def _is_last_video(self, _):
        return len(self._videos) == 0
