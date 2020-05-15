from collections import namedtuple
from dataclasses import astuple, dataclass
from enum import Enum, auto
from uuid import UUID

import structlog
from OpenCast.app.command import video as Cmd
from OpenCast.config import config
from OpenCast.domain.event import video as VideoEvt

from .workflow import Workflow


@dataclass
class Video:
    id: UUID
    source: str
    playlist_id: UUID

    def to_tuple(self):
        return astuple(self)


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

    def __init__(self, id, app_facade, video_repo, video: Video):
        logger = structlog.get_logger(__name__)
        super(VideoWorkflow, self).__init__(
            logger, self, id, app_facade, initial=VideoWorkflow.States.INITIAL,
        )
        self._video_repo = video_repo
        self._video = video
        self._with_priority = False

    def start(self, with_priority):
        self._with_priority = with_priority
        self._create()

    # States
    def on_enter_CREATING(self):
        self._observe_dispatch(
            VideoEvt.VideoCreated, Cmd.CreateVideo, *self._video.to_tuple()
        )

    def on_enter_IDENTIFYING(self, _):
        self._observe_dispatch(
            VideoEvt.VideoIdentified, Cmd.IdentifyVideo, self._video.id,
        )

    def on_enter_RETRIEVING(self, _):
        self._observe_dispatch(
            VideoEvt.VideoRetrieved,
            Cmd.RetrieveVideo,
            self._video.id,
            self._with_priority,
        )

    def on_enter_FINALISING(self, _):
        self._observe_dispatch(
            VideoEvt.VideoSubtitleFetched,
            Cmd.FetchVideoSubtitle,
            self._video.id,
            config["subtitle.language"],
        )

    def on_enter_DELETING(self, _):
        self._observe_dispatch(VideoEvt.VideoDeleted, Cmd.DeleteVideo, self._video.id)

    def on_enter_COMPLETED(self, *_):
        self._complete()

    def on_enter_ABORTED(self, _):
        self._abort()

    # Conditions
    def is_complete(self):
        return self._video_repo.exists(self._video.id)
