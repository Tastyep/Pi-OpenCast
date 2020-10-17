""" The application's workflow """

from collections import namedtuple
from enum import Enum, auto

import structlog

from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.command import playlist as PlaylistCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.domain.constant import PLAYER_PLAYLIST_NAME
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.service.identity import IdentityService

from .workflow import Workflow, make_cmd


class InitWorkflow(Workflow):
    Completed = namedtuple("InitWorkflowCompleted", ("id"))
    Aborted = namedtuple("InitWorkflowAborted", ("id"))

    # fmt: off
    class States(Enum):
        INITIAL = auto()
        CREATING_PLAYER = auto()
        PURGING_VIDEOS = auto()
        COMPLETED = auto()
        ABORTED = auto()

    # Trigger - Source - Dest - Conditions - Unless - Before - After - Prepare
    transitions = [
        ["start",             States.INITIAL,         States.PURGING_VIDEOS, "player_exists"],  # noqa: E501
        ["start",             States.INITIAL,         States.CREATING_PLAYER],
        ["_player_created",   States.CREATING_PLAYER, States.PURGING_VIDEOS],
        ["_video_deleted",    States.PURGING_VIDEOS,  States.COMPLETED,      "videos_purged"],  # noqa: E501
        ["_video_deleted",    States.PURGING_VIDEOS,  "="],

        ["_operation_error",  '*',                    States.ABORTED],
    ]
    # fmt: on

    def __init__(
        self,
        id,
        app_facade,
        data_facade,
    ):
        logger = structlog.get_logger(__name__)
        super().__init__(
            logger,
            self,
            id,
            app_facade,
            initial=InitWorkflow.States.INITIAL,
        )
        self._data_facade = data_facade

        self._player_repo = data_facade.player_repo
        self._video_repo = data_facade.video_repo

        self._missing_videos = []

    # States
    def on_enter_CREATING_PLAYER(self):
        playlist_id = IdentityService.id_playlist()
        cmd = make_cmd(PlaylistCmd.CreatePlaylist, playlist_id, PLAYER_PLAYLIST_NAME)
        self._cmd_dispatcher.dispatch(cmd)
        self._observe_dispatch(
            PlayerEvt.PlayerCreated,
            PlayerCmd.CreatePlayer,
            IdentityService.id_player(),
            playlist_id,
        )

    def on_enter_PURGING_VIDEOS(self, *_):
        if not self._missing_videos:
            videos = self._video_repo.list()
            self._missing_videos = [
                video.id
                for video in videos
                if video.path is None or not video.path.exists()
            ]
            if not self._missing_videos:
                self.to_COMPLETED()
                return

        video_id = self._missing_videos.pop()
        self._observe_dispatch(VideoEvt.VideoDeleted, VideoCmd.DeleteVideo, video_id)

    def on_enter_COMPLETED(self, *_):
        self._complete()

    def on_enter_ABORTED(self, *_):
        self._cancel()

    # Conditions
    def player_exists(self):
        return self._player_repo.exists(IdentityService.id_player())

    def videos_purged(self, *_):
        return len(self._missing_videos) == 0
