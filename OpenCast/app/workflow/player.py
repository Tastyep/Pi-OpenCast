""" Workflows running player related operations """

from collections import namedtuple
from enum import Enum, auto
from typing import List

import structlog

from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.command import playlist as PlaylistCmd
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.model import Id
from OpenCast.domain.service.identity import IdentityService

from .video import Video, VideoWorkflow
from .workflow import Workflow


class QueueVideoWorkflow(Workflow):
    Completed = namedtuple("QueueVideoWorkflowCompleted", ("id", "model_id"))
    Aborted = namedtuple("QueueVideoWorkflowAborted", ("id", "model_id"))

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
        ["_playlist_content_updated", States.QUEUEING,   States.COMPLETED],
        ["_operation_error",          States.QUEUEING,   States.ABORTED],
    ]
    # fmt: on

    def __init__(
        self,
        id,
        app_facade,
        data_facade,
        video: Video,
        queue_front: bool,
        prev_video_id: Id = None,
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=QueueVideoWorkflow.States.INITIAL,
        )
        self.video = video
        self._data_facade = data_facade
        self._queue_front = queue_front
        self._prev_video_id = prev_video_id
        self._player_playlist_id = self._data_facade.player_repo.get_player().queue

    # States
    def on_enter_COLLECTING(self):
        workflow_id = IdentityService.id_workflow(VideoWorkflow, self.video.id)
        workflow = self._factory.make_video_workflow(
            workflow_id, self._app_facade, self._data_facade, self.video
        )
        self._observe_start(workflow)

    def on_enter_QUEUEING(self, evt):
        self._observe_dispatch(
            PlaylistEvt.PlaylistContentUpdated,
            PlaylistCmd.QueueVideo,
            self._player_playlist_id,
            self.video.id,
            self._queue_front,
            self._prev_video_id,
        )

    def on_enter_COMPLETED(self, _):
        self._complete(self.video.id)

    def on_enter_ABORTED(self, _):
        self._cancel(self.video.id)


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
        data_facade,
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
        self.videos = videos[::-1]
        self._data_facade = data_facade

    def start(self):
        self._queue_videos(None)

    # States
    def on_enter_QUEUEING(self, _):
        video = self.videos.pop()
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, video.id)
        workflow = self._factory.make_queue_video_workflow(
            workflow_id,
            self._app_facade,
            self._data_facade,
            video,
            queue_front=False,
        )
        self._observe_start(workflow)

    def on_enter_COMPLETED(self, _):
        self._complete()

    def on_enter_ABORTED(self, _):
        self._cancel()

    # Conditions
    def _is_last_video(self, evt):
        return len(self.videos) == 0


class StreamVideoWorkflow(Workflow):
    Completed = namedtuple("StreamVideoWorkflowCompleted", ("id", "model_id"))
    Aborted = namedtuple("StreamVideoWorkflowAborted", ("id", "model_id"))

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

    def __init__(self, id, app_facade, data_facade, video: Video):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=StreamVideoWorkflow.States.INITIAL,
        )

        self.video = video
        self._data_facade = data_facade

    # States
    def on_enter_QUEUEING(self):
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, self.video.id)
        workflow = self._factory.make_queue_video_workflow(
            workflow_id,
            self._app_facade,
            self._data_facade,
            self.video,
            queue_front=False,
        )
        self._observe_start(workflow)

    def on_enter_STARTING(self, evt):
        self._observe_dispatch(
            PlayerEvt.PlayerStarted,
            PlayerCmd.PlayVideo,
            IdentityService.id_player(),
            self.video.id,
        )

    def on_enter_COMPLETED(self, _):
        self._complete(self.video.id)

    def on_enter_ABORTED(self, _):
        self._cancel(self.video.id)


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
        data_facade,
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

        self.videos = videos[::-1]
        self._data_facade = data_facade
        self._prev_video_id = None

    def start(self):
        self._play_video(None)

    # States
    def on_enter_STARTING(self, _):
        video = self.videos.pop()
        workflow_id = IdentityService.id_workflow(StreamVideoWorkflow, video.id)
        workflow = self._factory.make_stream_video_workflow(
            workflow_id, self._app_facade, self._data_facade, video
        )
        self._observe_start(
            workflow,
        )

    def on_enter_QUEUEING(self, evt):
        evt_type = type(evt)
        if evt_type in [StreamVideoWorkflow.Completed, QueueVideoWorkflow.Completed]:
            self._prev_video_id = evt.model_id

        video = self.videos.pop()
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, video.id)
        workflow = self._factory.make_queue_video_workflow(
            workflow_id,
            self._app_facade,
            self._data_facade,
            video,
            queue_front=True,
            prev_video_id=self._prev_video_id,
        )
        self._observe_start(
            workflow,
        )

    def on_enter_COMPLETED(self, _):
        self._complete()

    def on_enter_ABORTED(self, _):
        self._cancel()

    # Conditions
    def _is_last_video(self, _):
        return len(self.videos) == 0
