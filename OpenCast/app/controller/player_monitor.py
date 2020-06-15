import uuid

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
from OpenCast.util.conversion import str_to_bool

from .monitor import MonitorController


class PlayerMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade, service_factory):
        super().__init__(app_facade, infra_facade)

        media_factory = infra_facade.media_factory
        self._source_service = service_factory.make_source_service(
            media_factory.make_downloader(app_facade.evt_dispatcher),
            media_factory.make_video_parser(),
        )
        self._player_repo = data_facade.player_repo
        self._video_repo = data_facade.video_repo
        self._player_repo.create(Player(uuid.uuid4()))

        self._route("player/stream", callback=self._stream)
        self._route("player/queue", callback=self._queue)
        self._route("player/next", callback=self._next)
        self._route("player/prev", callback=self._prev)
        self._route("player/stop", callback=self._stop)
        self._route("player/pause", callback=self._pause)
        self._route("player/seek", callback=self._seek)
        self._route("player/volume", callback=self._volume)
        self._route("player/subtitle/toggle", callback=self._subtitle_toggle)
        self._route("player/subtitle/seek", callback=self._subtitle_seek)

    def _stream(self, request):
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

    def _queue(self, request):
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

    def _next(self, _):
        self._dispatch(Cmd.NextVideo)

    def _prev(self, _):
        self._dispatch(Cmd.PrevVideo)

    def _stop(self, _):
        self._dispatch(Cmd.StopPlayer)

    def _pause(self, _):
        self._dispatch(Cmd.ToggleVideoState)

    def _seek(self, request):
        forward = str_to_bool(request.query["forward"])
        long = str_to_bool(request.query["long"])
        side = 1 if forward is True else -1
        step = Player.LONG_TIME_STEP if long is True else Player.SHORT_TIME_STEP
        self._dispatch(Cmd.SeekVideo, side * step)

    def _volume(self, request):
        volume = int(request.query["value"])
        self._dispatch(Cmd.ChangeVolume, volume)

    def _subtitle_toggle(self, _):
        self._dispatch(Cmd.ToggleSubtitle)

    def _subtitle_seek(self, request):
        forward = str_to_bool(request.query["forward"])
        step = Player.SUBTITLE_DELAY_STEP if forward else -Player.SUBTITLE_DELAY_STEP
        self._dispatch(Cmd.IncreaseSubtitleDelay, step)

    def _dispatch(self, cmd_cls, *args, **kwargs):
        player_id = IdentityService.id_player()
        return super()._dispatch(cmd_cls, player_id, *args, **kwargs)
