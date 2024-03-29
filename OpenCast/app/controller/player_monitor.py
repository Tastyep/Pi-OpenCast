""" Player capabilities monitoring routes """

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import structlog
from aiohttp_apispec import docs

from OpenCast.app.command import player as Cmd
from OpenCast.app.notification import Level as NotifLevel
from OpenCast.app.notification import Notification
from OpenCast.app.service.error import OperationError
from OpenCast.app.workflow.player import (
    QueuePlaylistWorkflow,
    QueueVideoWorkflow,
    StreamPlaylistWorkflow,
    StreamVideoWorkflow,
    Video,
)
from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.model import Id
from OpenCast.domain.model.player import PlayerSchema
from OpenCast.domain.service.identity import IdentityService

from .monitor import MonitorController
from .monitoring_schema import ErrorSchema


class PlayerMonitController(MonitorController):
    """The controller in charge of player related requests"""

    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "/player")

        media_factory = infra_facade.media_factory
        self._source_service = service_factory.make_source_service(
            media_factory.make_downloader(app_facade.evt_dispatcher),
            media_factory.make_video_parser(),
        )
        self._data_facade = data_facade
        self._player_repo = data_facade.player_repo
        self._playlist_repo = data_facade.playlist_repo
        self._video_repo = data_facade.video_repo

        self._route("GET", "/", self.get)
        self._route("POST", "/stream", self.stream)
        self._route("POST", "/queue", self.queue)
        self._route("POST", "/play", self.play)
        self._route("POST", "/stop", self.stop)
        self._route("POST", "/pause", self.pause)
        self._route("POST", "/seek", self.seek)
        self._route("POST", "/volume", self.volume)
        self._route("POST", "/subtitle/toggle", self.subtitle_toggle)
        self._route("POST", "/subtitle/seek", self.subtitle_seek)

    @docs(
        tags=["player"],
        summary="Get player",
        description="Querie and return the media player",
        operationId="getPlayer",
        responses={
            200: {"description": "Successful operation", "schema": PlayerSchema},
        },
    )
    async def get(self, _):
        player = self._player_repo.get_player()
        return self._ok(player)

    @docs(
        tags=["player"],
        summary="Stream URL",
        description="Unpack, download and stream the media(s) referenced by the URL",
        operationId="streamMedia",
        parameters=[
            {
                "in": "query",
                "name": "url",
                "description": "URL of the media(s) to play",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            204: {"description": "Valid URL"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def stream(self, req):
        source = req.query["url"]
        video_id = IdentityService.id_video(source)
        playlist_id = self._player_repo.get_player().queue

        if self._source_service.is_playlist(source):
            collection_id = IdentityService.random()
            self._evt_dispatcher.dispatch(
                Notification(
                    collection_id,
                    NotifLevel.INFO,
                    "unfolding playlist",
                    {"source": source},
                )
            )

            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                sources = await loop.run_in_executor(
                    pool, partial(self._source_service.unfold, source)
                )
                if not sources:
                    return self._internal_error("Could not unfold the playlist URL")

                self._evt_dispatcher.dispatch(
                    Notification(
                        collection_id,
                        NotifLevel.INFO,
                        "downloading playlist",
                        {"source": source, "count": f"{len(sources)} media"},
                    )
                )
                videos = [
                    Video(IdentityService.id_video(source), source, collection_id)
                    for source in sources
                ]

                workflow_id = IdentityService.id_workflow(
                    StreamPlaylistWorkflow, video_id
                )
                self._start_workflow(
                    StreamPlaylistWorkflow,
                    workflow_id,
                    self._data_facade,
                    videos,
                    playlist_id,
                )
                return self._no_content()

        video = Video(video_id, source, collection_id=None)
        self._start_workflow(
            StreamVideoWorkflow, video_id, self._data_facade, video, playlist_id
        )

        return self._no_content()

    @docs(
        tags=["player"],
        summary="Queue URL",
        description="Unpack, download and queue the media(s) referenced by the URL",
        operationId="queueMedia",
        parameters=[
            {
                "in": "query",
                "name": "url",
                "description": "URL of the media(s) to queue",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            204: {"description": "Valid URL"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def queue(self, req):
        source = req.query["url"]
        video_id = IdentityService.id_video(source)
        playlist_id = self._player_repo.get_player().queue

        if self._source_service.is_playlist(source):
            collection_id = IdentityService.random()
            self._evt_dispatcher.dispatch(
                Notification(
                    collection_id,
                    NotifLevel.INFO,
                    "unfolding playlist",
                    {"source": source},
                )
            )

            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                sources = await loop.run_in_executor(
                    pool, partial(self._source_service.unfold, source)
                )
                if not sources:
                    return self._internal_error("Could not unfold the playlist URL")

                self._evt_dispatcher.dispatch(
                    Notification(
                        collection_id,
                        NotifLevel.INFO,
                        "downloading playlist",
                        {"source": source, "count": f"{len(sources)} media"},
                    )
                )
                videos = [
                    Video(IdentityService.id_video(source), source, collection_id)
                    for source in sources
                ]

                workflow_id = IdentityService.id_workflow(
                    QueuePlaylistWorkflow, video_id
                )
                self._start_workflow(
                    QueuePlaylistWorkflow,
                    workflow_id,
                    self._data_facade,
                    videos,
                    playlist_id,
                )
                return self._no_content()

        video = Video(video_id, source, collection_id=None)
        self._start_workflow(
            QueueVideoWorkflow,
            video_id,
            self._data_facade,
            video,
            playlist_id,
            queue_front=False,
        )

        return self._no_content()

    @docs(
        tags=["player"],
        summary="Play media",
        description="Play the media selected by ID",
        operationId="playMedia",
        parameters=[
            {
                "in": "query",
                "name": "id",
                "description": "ID of the media",
                "type": "string",
                "required": True,
            },
        ],
        responses={
            200: {"description": "Successful operation"},
            404: {"description": "Video not found"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def play(self, req):
        video_id = Id(req.query["id"])
        if not self._video_repo.exists(video_id):
            return self._not_found()

        playlist = self._playlist_repo.get(HOME_PLAYLIST.id)
        if video_id not in playlist.ids:
            return self._forbidden("the video is not queued")

        handlers, channel = self._make_default_handlers(PlayerEvt.PlayerStateUpdated)
        self._observe_dispatch(handlers, Cmd.PlayVideo, video_id)

        return await channel.receive()

    @docs(
        tags=["player"],
        summary="Stop player",
        description="Stop the media player",
        operationId="stopPlayer",
        responses={
            200: {"description": "Successful operation"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def stop(self, _):
        handlers, channel = self._make_default_handlers(PlayerEvt.PlayerStateUpdated)
        self._observe_dispatch(handlers, Cmd.StopPlayer)

        return await channel.receive()

    @docs(
        tags=["player"],
        summary="Pause player",
        description="Pause the media player",
        operationId="pausePlayer",
        responses={
            200: {"description": "Successful operation"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def pause(self, _):
        handlers, channel = self._make_default_handlers(PlayerEvt.PlayerStateUpdated)
        self._observe_dispatch(handlers, Cmd.TogglePlayerState)

        return await channel.receive()

    @docs(
        tags=["player"],
        summary="Seek media",
        description="Seek the active media with a given step",
        operationId="seekMedia",
        parameters=[
            {
                "in": "query",
                "name": "duration",
                "description": "The time in ms to seek the media to",
                "type": "integer",
                "required": True,
            },
        ],
        responses={
            200: {"description": "Successful operation"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def seek(self, req):
        duration = int(req.query["duration"])
        handlers, channel = self._make_default_handlers(PlayerEvt.VideoSeeked)
        self._observe_dispatch(handlers, Cmd.SeekVideo, duration)

        return await channel.receive()

    @docs(
        tags=["player"],
        summary="Update volume",
        description="Update the volume of the media player",
        operationId="updateVolume",
        parameters=[
            {
                "in": "query",
                "name": "value",
                "description": "The value for the player's volume [0-100]",
                "type": "integer",
                "format": "int32",
                "required": True,
            },
        ],
        responses={
            200: {"description": "Successful operation"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def volume(self, req):
        volume = int(req.query["value"])
        handlers, channel = self._make_default_handlers(PlayerEvt.VolumeUpdated)
        self._observe_dispatch(handlers, Cmd.UpdateVolume, volume)

        return await channel.receive()

    @docs(
        tags=["player"],
        summary="Toggle subtitle",
        description="Toggle the active media subtitle state",
        operationId="toggleMediaSubtitle",
        responses={
            200: {"description": "Successful operation"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def subtitle_toggle(self, _):
        handlers, channel = self._make_default_handlers(PlayerEvt.SubtitleStateUpdated)
        self._observe_dispatch(handlers, Cmd.ToggleSubtitle)

        return await channel.receive()

    @docs(
        tags=["player"],
        summary="Seek subtitle",
        description="Seek the active media subtitle with a given step",
        operationId="seekMediaSubtitle",
        parameters=[
            {
                "in": "query",
                "name": "forward",
                "description": "The time in ms to seek the subtitles",
                "type": "int",
                "required": True,
            }
        ],
        responses={
            200: {"description": "Successful operation"},
            500: {"description": "Internal error", "schema": ErrorSchema},
        },
    )
    async def subtitle_seek(self, req):
        duration = int(req.query["duration"])
        handlers, channel = self._make_default_handlers(PlayerEvt.SubtitleDelayUpdated)
        self._observe_dispatch(handlers, Cmd.UpdateSubtitleDelay, duration)

        return await channel.receive()

    def _make_default_handlers(self, evt_cls):
        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            player = self._player_repo.get_player()
            channel.send(self._ok(player))

        def on_error(evt):
            channel.send(self._internal_error(evt.error, evt.details))

        evtcls_handler = {evt_cls: on_success, OperationError: on_error}
        return evtcls_handler, channel

    def _observe_dispatch(self, evtcls_handler, cmd_cls, *args, **kwargs):
        player_id = IdentityService.id_player()
        super()._observe_dispatch(evtcls_handler, cmd_cls, player_id, *args, **kwargs)
