from collections import namedtuple
from enum import Enum, auto

import structlog
from OpenCast.app.command import video as Cmd
from OpenCast.config import config
from OpenCast.domain.event import video as VideoEvt

from .workflow import Workflow


class VideoWorkflow(Workflow):
    Completed = namedtuple("VideoWorkflowCompleted", ("id"))
    Aborted = namedtuple("VideoWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        CREATING = auto()
        IDENTIFYING = auto()
        RETRIEVING = auto()
        FINALISING = auto()
        COMPLETED = auto()
        DELETING = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_create",                 States.INITIAL,     States.COMPLETED,  "is_complete"],  # noqa: E501
        ["_create",                 States.INITIAL,     States.CREATING],
        ["_video_created",          States.CREATING,    States.IDENTIFYING],
        ["_video_identified",       States.IDENTIFYING, States.RETRIEVING],
        ["_video_retrieved",        States.RETRIEVING,  States.FINALISING],
        ["_video_subtitle_fetched", States.FINALISING,  States.COMPLETED],

        ["_operation_error",        States.CREATING,    States.ABORTED],
        ["_operation_error",        '*',                States.DELETING],
        ["_video_deleted",          States.DELETING,    States.ABORTED],
    ]
    # fmt: on

    def __init__(self, id, cmd_dispatcher, evt_dispatcher, video_repo, source_service):
        logger = structlog.get_logger(__name__)
        super(VideoWorkflow, self).__init__(
            logger,
            self,
            id,
            cmd_dispatcher,
            evt_dispatcher,
            initial=VideoWorkflow.States.INITIAL,
            send_event=True,
        )
        self._video_repo = video_repo
        self._source_service = source_service

    def start(self, video_id, source, playlist_id, with_priority):
        self._with_priority = with_priority
        self._create(video_id, source, playlist_id)

    # States
    def on_enter_CREATING(self, evt):
        self._observe_dispatch(
            VideoEvt.VideoCreated, Cmd.CreateVideo, *evt.args, **evt.kwargs
        )

    def on_enter_IDENTIFYING(self, evt):
        (evt,) = evt.args
        self._observe_dispatch(
            VideoEvt.VideoIdentified, Cmd.IdentifyVideo, evt.model_id,
        )

    def on_enter_RETRIEVING(self, evt):
        (evt,) = evt.args
        self._observe_dispatch(
            VideoEvt.VideoRetrieved,
            Cmd.RetrieveVideo,
            evt.model_id,
            self._with_priority,
        )

    def on_enter_FINALISING(self, evt):
        (evt,) = evt.args
        self._observe_dispatch(
            VideoEvt.VideoSubtitleFetched,
            Cmd.FetchVideoSubtitle,
            evt.model_id,
            config["subtitle.language"],
        )

    def on_enter_DELETING(self, evt):
        (error,) = evt.args
        self._observe_dispatch(
            VideoEvt.VideoDeleted, Cmd.DeleteVideo, error.cmd.model_id
        )

    def on_enter_COMPLETED(self, _):
        self._complete()

    def on_enter_ABORTED(self, _):
        self._abort()

    # Conditions
    def is_complete(self, evt):
        video_id = evt.args[0]
        return self._video_repo.exists(video_id)
