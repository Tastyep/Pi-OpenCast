from collections import namedtuple
from enum import Enum, auto
from pathlib import Path

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
        IDENTIFYING = auto()
        CREATING = auto()
        DOWNLOADING = auto()
        FINALISING = auto()
        COMPLETED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["_identify",               States.INITIAL,     States.COMPLETED,  "is_complete"],  # noqa: E501
        ["_identify",               States.INITIAL,     States.IDENTIFYING],
        ["_create",                 States.IDENTIFYING, States.CREATING],
        ["_video_created",          States.CREATING,    States.FINALISING, "is_disk_available"],  # noqa: E501
        ["_video_created",          States.CREATING,    States.DOWNLOADING],
        ["_video_downloaded",       States.DOWNLOADING, States.FINALISING],
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
        self._identify(video_id, source, playlist_id)

    # States
    def on_enter_IDENTIFYING(self, evt):
        (video_id, source, playlist_id) = evt.args
        # TODO: move this logic in video service
        # Handle errors with CommandFailure
        metadata = self._source_service.fetch_metadata(source)
        if "error" in metadata:
            self.cancel(video_id)
            return

        title = None
        path = None
        if metadata["online"] is False:
            path = Path(source)
            title = path.parent
        else:
            output_dir = config["downloader.output_directory"]
            title = metadata["title"]
            path = f"{output_dir}/{title}-{hash(source)}.mp4"

        self._create(video_id, source, playlist_id, title, path)

    def on_enter_CREATING(self, evt):
        self._observe_dispatch(
            VideoEvt.VideoCreated, Cmd.AddVideo, *evt.args, **evt.kwargs
        )

    def on_enter_DOWNLOADING(self, evt):
        (evt,) = evt.args
        self._observe_dispatch(
            VideoEvt.VideoDownloaded,
            Cmd.DownloadVideo,
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

    # Conditions
    def is_disk_available(self, evt):
        (evt,) = evt.args
        return evt.path.is_file()

    def is_complete(self, evt):
        video_id = evt.args[0]
        return self._video_repo.exists(video_id)
