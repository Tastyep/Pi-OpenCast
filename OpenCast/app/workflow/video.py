""" Workflows running video related operations """

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

import structlog

from OpenCast.app.command import video as Cmd
from OpenCast.app.notification import Level as NotifLevel
from OpenCast.app.notification import Notification
from OpenCast.app.service.error import OperationError
from OpenCast.config import settings
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model import Id
from OpenCast.infra.media.downloader import Options as DownloadOptions

from .workflow import Workflow


@dataclass
class Video:
    id: Id
    source: str
    collection_id: Optional[Id]
    dl_opts: DownloadOptions

    def to_tuple(self):
        return (self.id, self.source, self.collection_id)


class VideoWorkflow(Workflow):
    Completed = namedtuple("VideoWorkflowCompleted", ("id", "model_id"))
    Aborted = namedtuple("VideoWorkflowAborted", ("id", "model_id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        CREATING = auto()
        RETRIEVING = auto()
        PARSING = auto()
        SUB_RETRIEVING = auto()
        FINALIZING = auto()
        COMPLETED = auto()
        DELETING = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_create",                 States.INITIAL,        States.COMPLETED,  "is_complete"],  # noqa: E501
        ["_create",                 States.INITIAL,        States.CREATING],
        ["_video_created",          States.CREATING,       States.RETRIEVING],
        ["_video_retrieved",        States.RETRIEVING,     States.FINALIZING,  "is_stream"],  # noqa: E501
        ["_video_retrieved",        States.RETRIEVING,     States.PARSING],
        ["_video_parsed",           States.PARSING,        States.FINALIZING,  "subtitle_disabled"],  # noqa: E501
        ["_video_parsed",           States.PARSING,        States.SUB_RETRIEVING],
        ["_video_subtitle_fetched", States.SUB_RETRIEVING, States.FINALIZING],
        ["_video_state_updated",    States.FINALIZING,     States.COMPLETED],

        ["_operation_error",        States.CREATING,       States.ABORTED],
        ["_operation_error",        '*',                   States.DELETING],
        ["_video_deleted",          States.DELETING,       States.ABORTED],
    ]
    # fmt: on

    def __init__(self, id, app_facade, data_facade, video: Video):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            id,
            app_facade,
            initial=VideoWorkflow.States.INITIAL,
        )
        self._video_repo = data_facade.video_repo
        self._video = video

    def start(self):
        self._create()

    # States
    def on_enter_CREATING(self):
        self._observe_dispatch(
            VideoEvt.VideoCreated,
            Cmd.CreateVideo,
            self._video.id,
            self._video.source,
            self._video.collection_id,
        )

    def on_enter_RETRIEVING(self, _):
        self._observe_dispatch(
            VideoEvt.VideoRetrieved,
            Cmd.RetrieveVideo,
            self._video.id,
            settings["downloader.output_directory"],
            self._video.dl_opts,
        )

    def on_enter_PARSING(self, _):
        self._observe_dispatch(
            VideoEvt.VideoParsed,
            Cmd.ParseVideo,
            self._video.id,
        )

    def on_enter_SUB_RETRIEVING(self, evt):
        self._observe_dispatch(
            VideoEvt.VideoSubtitleFetched,
            Cmd.FetchVideoSubtitle,
            self._video.id,
            settings["subtitle.language"],
        )

    def on_enter_FINALIZING(self, _):
        self._observe_dispatch(
            VideoEvt.VideoStateUpdated,
            Cmd.SetVideoReady,
            self._video.id,
        )

    def on_enter_DELETING(self, evt):
        self._evt_dispatcher.dispatch(
            Notification(evt.id, NotifLevel.ERROR, evt.error, evt.details)
        )
        self._observe_dispatch(VideoEvt.VideoDeleted, Cmd.DeleteVideo, self._video.id)

    def on_enter_COMPLETED(self, *_):
        self._complete(self._video.id)

    def on_enter_ABORTED(self, evt):
        if isinstance(evt, OperationError):
            self._evt_dispatcher.dispatch(
                Notification(evt.id, NotifLevel.ERROR, evt.error, evt.details)
            )
        self._cancel(self._video.id)

    # Conditions
    def is_complete(self):
        return self._video_repo.exists(self._video.id)

    def is_stream(self, _):
        return self._video_repo.get(self._video.id).streamable()

    def subtitle_disabled(self, _):
        return not settings["subtitle.enabled"]
