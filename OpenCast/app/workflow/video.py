from collections import namedtuple
from enum import Enum, auto

from OpenCast.app.command import video as Cmd
from OpenCast.config import config
from OpenCast.domain.event import video as VideoEvt

from .workflow import Workflow


class VideoWorkflow(Workflow):
    Completed = namedtuple("VideoWorkflowCompleted", ("id", "video_id"))
    Aborted = namedtuple("VideoWorkflowAborted", ("id", "video_id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        CREATING = auto()
        IDENTIFYING = auto()
        RETRIEVING = auto()
        FINALISING = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_create",                 States.INITIAL,     States.COMPLETED,  "is_complete"],  # noqa: E501
        ["_create",                 States.INITIAL,     States.CREATING],
        ["_video_created",          States.CREATING,    States.IDENTIFYING],
        ["_video_identified",       States.IDENTIFYING, States.RETRIEVING],
        ["_video_retrieved",        States.RETRIEVING,  States.FINALISING],
        ["_video_subtitle_fetched", States.FINALISING,  States.COMPLETED],
    ]
    # fmt: on

    def __init__(self, id, cmd_dispatcher, evt_dispatcher, video_repo, source_service):
        super(VideoWorkflow, self).__init__(
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

    def on_enter_COMPLETED(self, evt):
        model_id = None
        if self.States[evt.transition.source] is self.States.INITIAL:
            model_id = evt.args[0]
        else:
            model_id = evt.args[0].model_id
        self._complete(model_id)

    def on_enter_ABORTED(self, evt):
        self._abort(evt.video_id)

    # Conditions
    def is_complete(self, evt):
        video_id = evt.args[0]
        return self._video_repo.exists(video_id)
