import uuid

from bottle import request
from OpenCast.app.command import player as Cmd
from OpenCast.app.workflow.player import (
    QueuePlaylistWorkflow,
    QueueVideoWorkflow,
    StreamPlaylistWorkflow,
    StreamVideoWorkflow,
    Video,
)
from OpenCast.domain.model.player import Player
from OpenCast.domain.service.identity import IdentityService

from .controller import Controller


class PlayerMonitController(Controller):
    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        super(PlayerMonitController, self).__init__(app_facade)

        media_factory = infra_facade.media_factory
        self._source_service = service_factory.make_source_service(
            media_factory.make_downloader(app_facade.evt_dispatcher),
            media_factory.make_video_parser(),
        )
        self._player_repo = data_facade.player_repo
        self._video_repo = data_facade.video_repo
        self._player_repo.create(Player(uuid.uuid4()))

        # TODO add video monit controller
        server = infra_facade.server

        def route(url, callback):
            server.route(f"/api/player/{url}", callback=callback)

        route("stream", self._stream)
        route("queue", self._queue)
        route("video", self._video)
        route("subtitle", self._subtitle)
        route("sound", self._sound)
        route("running", self._running)

    def _stream(self):
        source = request.query["url"]
        if self._source_service.is_playlist(source):
            sources = self._source_service.unfold(source)
            playlist_id = IdentityService.id_playlist(source)
            videos = [
                Video(IdentityService.id_video(source), source, playlist_id)
                for source in sources
            ]

            self._start_workflow(
                StreamPlaylistWorkflow, playlist_id, self._video_repo, videos
            )
            return

        video_id = IdentityService.id_video(source)
        video = Video(video_id, source, None)
        self._start_workflow(StreamVideoWorkflow, video_id, self._video_repo, video)

        return "1"

    def _queue(self):
        source = request.query["url"]
        if self._source_service.is_playlist(source):
            sources = self._source_service.unfold(source)
            playlist_id = IdentityService.id_playlist(source)
            videos = [
                Video(IdentityService.id_video(source), source, playlist_id)
                for source in sources
            ]

            self._start_workflow(
                QueuePlaylistWorkflow, playlist_id, self._video_repo, videos
            )
            return

        video_id = IdentityService.id_video(source)
        video = Video(video_id, source, None)
        self._start_workflow(QueueVideoWorkflow, video_id, self._video_repo, video)

    def _video(self):
        control = request.query["control"]
        if control == "pause":
            self._dispatch(Cmd.ToggleVideoState)
        elif control == "stop":
            self._dispatch(Cmd.StopPlayer)
        elif control == "right":
            self._dispatch(Cmd.SeekVideo, Player.SHORT_TIME_STEP)
        elif control == "left":
            self._dispatch(Cmd.SeekVideo, -Player.SHORT_TIME_STEP)
        elif control == "longright":
            self._dispatch(Cmd.SeekVideo, Player.LONG_TIME_STEP)
        elif control == "longleft":
            self._dispatch(Cmd.SeekVideo, -Player.LONG_TIME_STEP)
        elif control == "prev":
            self._dispatch(Cmd.PrevVideo)
        elif control == "next":
            self._dispatch(Cmd.NextVideo)
        else:
            return "0"

        return "1"

    def _sound(self):
        if request.query["vol"] == "more":
            self._dispatch(Cmd.ChangeVolume, Player.VOLUME_STEP)
        else:
            self._dispatch(Cmd.ChangeVolume, -Player.VOLUME_STEP)
        return "1"

    def _subtitle(self):
        action = request.query["action"]

        if action == "toggle":
            self._dispatch(Cmd.ToggleSubtitle)
        elif action == "increase":
            self._dispatch(Cmd.IncreaseSubtitleDelay, Player.SUBTITLE_DELAY_STEP)
        elif action == "decrease":
            self._dispatch(Cmd.DecreaseSubtitleDelay, -Player.SUBTITLE_DELAY_STEP)

    def _running(self):
        return 1

    def _dispatch(self, cmd_cls, *args, **kwargs):
        player_id = IdentityService.id_player()
        return super(PlayerMonitController, self)._dispatch(
            cmd_cls, player_id, *args, **kwargs
        )
