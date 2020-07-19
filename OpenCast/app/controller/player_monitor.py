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
        super().__init__(app_facade, infra_facade, "/player")

        media_factory = infra_facade.media_factory
        self._source_service = service_factory.make_source_service(
            media_factory.make_downloader(app_facade.evt_dispatcher),
            media_factory.make_video_parser(),
        )
        self._player_repo = data_facade.player_repo
        self._video_repo = data_facade.video_repo
        self._player_repo.create(Player(uuid.uuid4()))

        self._route("/", method="GET", callback=self._get)
        self._route("/stream", method="POST", callback=self._stream)
        self._route("/queue", method="POST", callback=self._queue)
        self._route("/video", method="POST", callback=self._pick_video)
        self._route("/stop", method="POST", callback=self._stop)
        self._route("/pause", method="POST", callback=self._pause)
        self._route("/seek", method="POST", callback=self._seek)
        self._route("/volume", method="POST", callback=self._volume)
        self._route("/subtitle/toggle", method="POST", callback=self._subtitle_toggle)
        self._route("/subtitle/seek", method="POST", callback=self._subtitle_seek)

    def _get(self, _):
        player = self._player_repo.get_player()
        return self._make_response(200, player)

    def _stream(self, req):
        source = req.query["url"]
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

    def _queue(self, req):
        source = req.query["url"]
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

    def _pick_video(self, req):
        video_id = uuid.UUID(req.query["video_id"])
        self._dispatch(Cmd.PickVideo, video_id)

    def _stop(self, _):
        self._dispatch(Cmd.StopPlayer)

    def _pause(self, _):
        self._dispatch(Cmd.ToggleVideoState)

    def _seek(self, req):
        forward = str_to_bool(req.query["forward"])
        long = str_to_bool(req.query["long"])
        side = 1 if forward is True else -1
        step = Player.LONG_TIME_STEP if long is True else Player.SHORT_TIME_STEP
        self._dispatch(Cmd.SeekVideo, side * step)

    def _volume(self, req):
        volume = int(req.query["value"])
        self._dispatch(Cmd.ChangeVolume, volume)

    def _subtitle_toggle(self, _):
        self._dispatch(Cmd.ToggleSubtitle)

    def _subtitle_seek(self, req):
        forward = str_to_bool(req.query["forward"])
        step = Player.SUBTITLE_DELAY_STEP if forward else -Player.SUBTITLE_DELAY_STEP
        self._dispatch(Cmd.IncreaseSubtitleDelay, step)

    def _dispatch(self, cmd_cls, *args, **kwargs):
        player_id = IdentityService.id_player()
        return super()._dispatch(cmd_cls, player_id, *args, **kwargs)
