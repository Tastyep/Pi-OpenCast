""" Workflows running player related operations """

from collections import namedtuple
from enum import Enum, auto
from typing import List

import structlog

from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.command import playlist as PlaylistCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model import Id as ModelId
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
        REMOVING = auto()
        QUEUEING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["start",                     States.INITIAL,    States.COLLECTING],

        ["_video_created",            States.COLLECTING, States.QUEUEING],
        ["_video_workflow_completed", States.COLLECTING, States.REMOVING, "is_queued"],
        ["_video_workflow_completed", States.COLLECTING, States.QUEUEING],
        ["_video_workflow_aborted",   States.COLLECTING, States.ABORTED],

        ["_playlist_content_updated", States.REMOVING,   States.QUEUEING],

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
        playlist_id: ModelId,
        queue_front: bool,
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            id,
            app_facade,
            initial=QueueVideoWorkflow.States.INITIAL,
        )
        self.video = video
        self.playlist_id = playlist_id
        self._queue_front = queue_front
        self._data_facade = data_facade

    # States
    def on_enter_COLLECTING(self):
        workflow_id = IdentityService.id_workflow(VideoWorkflow, self.video.id)
        workflow = self._factory.make_video_workflow(
            workflow_id, self._app_facade, self._data_facade, self.video
        )

        create_cmd_id = IdentityService.id_command(VideoCmd.CreateVideo, self.video.id)
        self._observe_group(
            {
                workflow_id: [workflow.Completed, workflow.Aborted],
                create_cmd_id: [VideoEvt.VideoCreated],
            },
        )
        self._start_workflow(workflow)

    def on_enter_REMOVING(self, _):
        playlist = self._data_facade.playlist_repo.get(self.playlist_id)
        playlist.ids.remove(self.video.id)
        self._observe_dispatch(
            PlaylistEvt.PlaylistContentUpdated,
            PlaylistCmd.UpdatePlaylistContent,
            self.playlist_id,
            playlist.ids,
        )

    def on_enter_QUEUEING(self, _):
        self._observe_dispatch(
            PlaylistEvt.PlaylistContentUpdated,
            PlaylistCmd.QueueVideo,
            self.playlist_id,
            self.video.id,
            self._queue_front,
        )

    def on_enter_COMPLETED(self, _):
        self._complete(self.video.id)

    def on_enter_ABORTED(self, _):
        self._cancel(self.video.id)

    # Conditions
    def is_queued(self, _):
        playlist = self._data_facade.playlist_repo.get(self.playlist_id)
        return self.video.id in playlist.ids


class QueuePlaylistWorkflow(Workflow):
    Completed = namedtuple("QueuePlaylistWorkflowCompleted", ("id"))
    Aborted = namedtuple("QueuePlaylistWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        QUEUEING = auto()
        COMPLETED = auto()

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
        playlist_id: ModelId,
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            id,
            app_facade,
            initial=StreamVideoWorkflow.States.INITIAL,
        )
        self.videos = videos[::-1]
        self.playlist_id = playlist_id
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
            self.playlist_id,
            queue_front=False,
        )
        self._observe_start(workflow)

    def on_enter_COMPLETED(self, _):
        self._complete()

    # Conditions
    def _is_last_video(self, _):
        return len(self.videos) == 0


class StreamVideoWorkflow(Workflow):
    Completed = namedtuple("StreamVideoWorkflowCompleted", ("id", "model_id"))
    Aborted = namedtuple("StreamVideoWorkflowAborted", ("id", "model_id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        QUEUEING = auto()
        SYNCHRONIZING = auto()
        STARTING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["start",                           States.INITIAL,         States.QUEUEING],

        ["_video_workflow_completed",       States.QUEUEING,        States.SYNCHRONIZING],   # noqa: E501
        ["_queue_video_workflow_completed", States.QUEUEING,        States.SYNCHRONIZING],   # noqa: E501
        ["_queue_video_workflow_aborted",   States.QUEUEING,        States.ABORTED],

        ["_video_workflow_completed",       States.SYNCHRONIZING,   States.STARTING],
        ["_queue_video_workflow_completed", States.SYNCHRONIZING,   States.STARTING],
        ["_queue_video_workflow_aborted",   States.SYNCHRONIZING,   States.ABORTED],

        ["_player_state_updated",           States.STARTING,        States.COMPLETED],
        ["_operation_error",                States.STARTING,        States.ABORTED],
    ]
    # fmt: on

    def __init__(self, id, app_facade, data_facade, video: Video, playlist_id: ModelId):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            id,
            app_facade,
            initial=StreamVideoWorkflow.States.INITIAL,
        )

        self.video = video
        self.playlist_id = playlist_id
        self._data_facade = data_facade

    # States
    def on_enter_QUEUEING(self):
        queue_workflow_id = IdentityService.id_workflow(
            QueueVideoWorkflow, self.video.id
        )
        queue_workflow = self._factory.make_queue_video_workflow(
            queue_workflow_id,
            self._app_facade,
            self._data_facade,
            self.video,
            self.playlist_id,
            queue_front=True,
        )

        video_workflow_id = IdentityService.id_workflow(VideoWorkflow, self.video.id)
        self._observe(
            video_workflow_id,
            [VideoWorkflow.Completed],
        )
        self._observe_start(queue_workflow)

    def on_enter_SYNCHRONIZING(self, _):
        pass

    def on_enter_STARTING(self, _):
        self._observe_dispatch(
            PlayerEvt.PlayerStateUpdated,
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
        playlist_id: ModelId,
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            id,
            app_facade,
            initial=StreamVideoWorkflow.States.INITIAL,
        )

        self.videos = videos[::-1]
        self.playlist_id = playlist_id
        self._data_facade = data_facade

    def start(self):
        self._play_video(None)

    # States
    def on_enter_STARTING(self, _):
        video = self.videos.pop()
        workflow_id = IdentityService.id_workflow(StreamVideoWorkflow, video.id)
        workflow = self._factory.make_stream_video_workflow(
            workflow_id, self._app_facade, self._data_facade, video, self.playlist_id
        )
        self._observe_start(
            workflow,
        )

    def on_enter_QUEUEING(self, _):
        video = self.videos.pop()
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, video.id)
        workflow = self._factory.make_queue_video_workflow(
            workflow_id,
            self._app_facade,
            self._data_facade,
            video,
            self.playlist_id,
            queue_front=True,
        )
        self._observe_start(
            workflow,
        )

    def on_enter_COMPLETED(self, _):
        self._complete()

    # Conditions
    def _is_last_video(self, _):
        return len(self.videos) == 0
