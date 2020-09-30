""" The application's workflow """

import traceback
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path

import structlog

from OpenCast.config import config
from OpenCast.domain.service.identity import IdentityService

from .video import Video, VideoWorkflow
from .workflow import Workflow


class RootWorkflow(Workflow):
    Completed = namedtuple("RootWorkflowCompleted", ("id"))
    Aborted = namedtuple("RootWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        LOADING = auto()
        RUNNING = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["start", States.INITIAL, States.LOADING],
    ]
    # fmt: on

    def __init__(
        self,
        id,
        app_facade,
        infra_facade,
        data_facade,
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=RootWorkflow.States.INITIAL,
        )
        self._infra_facade = infra_facade
        self._data_facade = data_facade

        self._file_service = infra_facade.service_factory.make_file_service()

    # States
    def on_enter_LOADING(self):
        # TODO: move this logic in a separate task and spawn a new one from here
        download_dir = Path(config["downloader.output_directory"])
        files = self._file_service.list_directory(download_dir, "*")
        for path in files:
            if not path.is_file():
                continue
            source = str(path)
            media_id = IdentityService.id_video(source)
            workflow_id = IdentityService.id_workflow(VideoWorkflow, media_id)
            workflow = self._factory.make_video_workflow(
                workflow_id,
                self._app_facade,
                self._data_facade.video_repo,
                Video(media_id, source, None),
            )
            self._start_workflow(workflow)

        self.to_RUNNING()

    def on_enter_RUNNING(self):
        try:
            self._infra_facade.server.start(
                config["server.host"], config["server.port"]
            )
        except Exception as e:
            self._logger.error(
                "Server exception caught", error=e, traceback=traceback.format_exc()
            )
            self.to_ABORTED(e)

    def on_enter_ABORTED(self, _):
        self.cancel()
