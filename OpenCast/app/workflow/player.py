from collections import namedtuple
from enum import Enum, auto

from OpenCast.app.command import player as PlayerCmd
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.service.identity import IdentityService

from .video import VideoWorkflow
from .workflow import Workflow


class QueueVideoWorkflow(Workflow):
    Completed = namedtuple("QueueVideoWorkflowCompleted", ("id", "video_id"))
    Aborted = namedtuple("QueueVideoWorkflowAborted", ("id", "video_id"))

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
    ]
    # fmt: on

    def __init__(self, id, cmd_dispatcher, evt_dispatcher, video_repo, source_service):
        super(QueueVideoWorkflow, self).__init__(
            self,
            id,
            cmd_dispatcher,
            evt_dispatcher,
            initial=QueueVideoWorkflow.States.INITIAL,
        )
        self._video_workflow = self._child_workflow(
            VideoWorkflow, video_repo, source_service
        )

    # States
    def on_enter_COLLECTING(self, video_id, source, playlist_id):
        self._observe_start(
            self._video_workflow, video_id, source, playlist_id, with_priority=False
        )

    def on_enter_QUEUEING(self, evt):
        self._observe_dispatch(
            PlayerEvt.VideoQueued,
            PlayerCmd.QueueVideo,
            IdentityService.id_player(),
            evt.video_id,
        )

    def on_enter_COMPLETED(self, evt):
        self._complete(evt.video_id)

    def on_enter_ABORTED(self, evt):
        self._abort(evt.video_id)


class QueuePlaylistWorkflow(Workflow):
    Completed = namedtuple("QueuePlaylistWorkflowCompleted", ("id", "playlist_id"))
    Aborted = namedtuple("QueuePlaylistWorkflowAborted", ("id", "playlist_id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        QUEUEING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_queue_videos",                   States.INITIAL,  States.QUEUEING],
        ["_queue_video_workflow_completed", States.QUEUEING, States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_completed", States.QUEUEING, "="],
        ["_queue_video_workflow_aborted",   States.QUEUEING, States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_aborted",   States.QUEUEING, "="],
    ]
    # fmt: on

    def __init__(self, id, cmd_dispatcher, evt_dispatcher, video_repo, source_service):
        super(QueuePlaylistWorkflow, self).__init__(
            self,
            id,
            cmd_dispatcher,
            evt_dispatcher,
            initial=StreamVideoWorkflow.States.INITIAL,
        )
        self._queue_video_workflow = self._child_workflow(
            QueueVideoWorkflow, video_repo, source_service
        )

    def start(self, video_ids, sources, playlist_id):
        self._video_ids = video_ids
        self._sources = sources
        self._playlist_id = playlist_id
        self._queue_videos(None)

    # States
    def on_enter_QUEUEING(self, evt):
        i = 0 if evt is None else self._video_ids.index(evt.video_id) + 1
        self._queue_video_workflow.reset()
        self._observe_start(
            self._queue_video_workflow,
            self._video_ids[i],
            self._sources[i],
            self._playlist_id,
        )

    def on_enter_COMPLETED(self, evt):
        self._complete(evt.video_id)

    def on_enter_ABORTED(self, evt):
        self._abort(evt.video_id)

    # Conditions
    def _is_last_video(self, evt):
        return evt.video_id == self._video_ids[-1]


class StreamVideoWorkflow(Workflow):
    Completed = namedtuple("StreamVideoWorkflowCompleted", ("id", "video_id"))
    Aborted = namedtuple("StreamVideoWorkflowAborted", ("id", "video_id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        COLLECTING = auto()
        STARTING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["start",                     States.INITIAL,    States.COLLECTING],
        ["_video_workflow_completed", States.COLLECTING, States.STARTING],
        ["_video_workflow_aborted",   States.COLLECTING, States.ABORTED],
        ["_player_started",           States.STARTING,   States.COMPLETED],
    ]
    # fmt: on

    def __init__(self, id, cmd_dispatcher, evt_dispatcher, video_repo, source_service):
        super(StreamVideoWorkflow, self).__init__(
            self,
            id,
            cmd_dispatcher,
            evt_dispatcher,
            initial=StreamVideoWorkflow.States.INITIAL,
        )

        self._video_workflow = self._child_workflow(
            VideoWorkflow, video_repo, source_service
        )

    # States
    def on_enter_COLLECTING(self, video_id, source, playlist_id):
        self._observe_start(
            self._video_workflow, video_id, source, playlist_id, with_priority=True
        )

    def on_enter_STARTING(self, evt):
        self._observe_dispatch(
            PlayerEvt.PlayerStarted,
            PlayerCmd.PlayVideo,
            IdentityService.id_player(),
            evt.video_id,
        )

    def on_enter_COMPLETED(self, evt):
        self._complete(evt.video_id)

    def on_enter_ABORTED(self, evt):
        self._abort(evt.video_id)


class StreamPlaylistWorkflow(Workflow):
    Completed = namedtuple("StreamPlaylistWorkflowCompleted", ("id", "playlist_id"))
    Aborted = namedtuple("StreamPlaylistWorkflowAborted", ("id", "playlist_id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        PLAYING = auto()
        QUEUEING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_play_video",                      States.INITIAL,  States.PLAYING],
        ["_stream_video_workflow_completed", States.PLAYING,  States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_stream_video_workflow_completed", States.PLAYING,  States.QUEUEING],
        ["_stream_video_workflow_aborted",   States.PLAYING,  States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_stream_video_workflow_aborted",   States.PLAYING,  "="],

        ["_queue_video_workflow_completed", States.QUEUEING,  States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_completed", States.QUEUEING,  "="],
        ["_queue_video_workflow_aborted",   States.QUEUEING,  States.COMPLETED, "_is_last_video"],  # noqa: E501
        ["_queue_video_workflow_aborted",   States.QUEUEING,  "="],
    ]
    # fmt: on

    def __init__(self, id, cmd_dispatcher, evt_dispatcher, video_repo, source_service):
        super(StreamPlaylistWorkflow, self).__init__(
            self,
            id,
            cmd_dispatcher,
            evt_dispatcher,
            initial=StreamVideoWorkflow.States.INITIAL,
        )
        self._stream_video_workflow = self._child_workflow(
            StreamVideoWorkflow, video_repo, source_service
        )
        self._queue_video_workflow = self._child_workflow(
            QueueVideoWorkflow, video_repo, source_service
        )

    def start(self, video_ids, sources, playlist_id):
        self._video_ids = video_ids
        self._sources = sources
        self._playlist_id = playlist_id
        self._play_video(None)

    # States
    def on_enter_PLAYING(self, evt):
        i = 0 if evt is None else self._video_ids.index(evt.video_id) + 1
        self._stream_video_workflow.reset()
        self._observe_start(
            self._stream_video_workflow,
            self._video_ids[i],
            self._sources[i],
            self._playlist_id,
        )

    def on_enter_QUEUEING(self, evt):
        i = self._video_ids.index(evt.video_id) + 1
        self._queue_video_workflow.reset()
        self._observe_start(
            self._queue_video_workflow,
            self._video_ids[i],
            self._sources[i],
            self._playlist_id,
        )

    def on_enter_COMPLETED(self, evt):
        self._complete(evt.video_id)

    def on_enter_ABORTED(self, evt):
        self._abort(evt.video_id)

    # Conditions
    def _is_last_video(self, evt):
        return evt.video_id == self._video_ids[-1]
