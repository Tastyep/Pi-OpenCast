import uuid

from bottle import request
from OpenCast.app.command import player as Cmd
from OpenCast.app.workflow.player import (
    QueuePlaylistWorkflow,
    QueueVideoWorkflow,
    StreamPlaylistWorkflow,
    StreamVideoWorkflow,
)
from OpenCast.domain.model.player import Player
from OpenCast.domain.service.identity import IdentityService

from .controller import Controller


class PlayerMonitController(Controller):
    def __init__(self, app_facade, data_facade, io_facade, service_factory):
        super(PlayerMonitController, self).__init__(app_facade)

        self._source_service = service_factory.make_source_service(
            io_facade.video_downloader()
        )
        self._player_repo = data_facade.player_repo()
        self._video_repo = data_facade.video_repo()
        self._player_repo.create(Player(uuid.uuid4()))

        # TODO add video monit controller
        server = io_facade.server()
        server.route("/stream", callback=self._stream)
        server.route("/queue", callback=self._queue)
        server.route("/video", callback=self._video)
        server.route("/subtitle", callback=self._subtitle)
        server.route("/sound", callback=self._sound)
        server.route("/running", callback=self._running)

    def _stream(self):
        source = request.query["url"]
        if self._source_service.is_playlist(source):
            sources = self._source_service.unfold(source)
            video_ids = [IdentityService.id_video(source) for source in sources]
            playlist_id = IdentityService.id_playlist(source)

            workflow_id = IdentityService.id_workflow(
                StreamPlaylistWorkflow, playlist_id
            )
            workflow = StreamPlaylistWorkflow(
                playlist_id,
                self._cmd_dispatcher,
                self._evt_dispatcher,
                self._video_repo,
                self._source_service,
            )
            workflow.start(video_ids, sources, playlist_id)
            return

        video_id = IdentityService.id_video(source)
        workflow_id = IdentityService.id_workflow(StreamVideoWorkflow, video_id)
        workflow = StreamVideoWorkflow(
            workflow_id,
            self._cmd_dispatcher,
            self._evt_dispatcher,
            self._video_repo,
            self._source_service,
        )
        workflow.start(video_id, source=source, playlist_id=None)

        return "1"

    def _queue(self):
        source = request.query["url"]
        if self._source_service.is_playlist(source):
            sources = self._source_service.unfold(source)
            video_ids = [IdentityService.id_video(source) for source in sources]
            playlist_id = IdentityService.id_playlist(source)

            workflow_id = IdentityService.id_workflow(
                QueuePlaylistWorkflow, playlist_id
            )
            workflow = QueuePlaylistWorkflow(
                workflow_id,
                self._cmd_dispatcher,
                self._evt_dispatcher,
                self._video_repo,
                self._source_service,
            )
            workflow.start(video_ids, sources, playlist_id)
            return

        video_id = IdentityService.id_video(source)
        workflow_id = IdentityService.id_workflow(QueueVideoWorkflow, video_id)
        workflow = QueueVideoWorkflow(
            workflow_id,
            self._cmd_dispatcher,
            self._evt_dispatcher,
            self._video_repo,
            self._source_service,
        )
        workflow.start(video_id, source, playlist_id=None)

    def _video(self):
        control = request.query["control"]
        cmd = None

        if control == "pause":
            cmd = self._make_cmd(Cmd.ToggleVideoState)
        elif control == "stop":
            cmd = self._make_cmd(Cmd.StopVideo)
        elif control == "right":
            cmd = self._make_cmd(Cmd.SeekVideo, 30)
        elif control == "left":
            cmd = self._make_cmd(Cmd.SeekVideo, -30)
        elif control == "longright":
            cmd = self._make_cmd(Cmd.SeekVideo, 300)
        elif control == "longleft":
            cmd = self._make_cmd(Cmd.SeekVideo, -300)
        elif control == "prev":
            cmd = self._make_cmd(Cmd.PrevVideo)
        elif control == "next":
            cmd = self._make_cmd(Cmd.NextVideo)
        else:
            return "0"

        self._cmd_dispatcher.dispatch(cmd)
        return "1"

    def _sound(self):
        cmd = None
        if request.query["vol"] == "more":
            cmd = self._make_cmd(Cmd.ChangeVolume, 10)
        else:
            cmd = self._make_cmd(Cmd.ChangeVolume, -10)

        self._cmd_dispatcher.dispatch(cmd)
        return "1"

    def _subtitle(self):
        action = request.query["action"]

        if action == "toggle":
            self._cmd_dispatcher.dispatch(self._make_cmd(Cmd.ToggleSubtitle))
        elif action == "increase":
            self._cmd_dispatcher.dispatch(self._make_cmd(Cmd.IncreaseSubtitleDelay))
        elif action == "decrease":
            self._cmd_dispatcher.dispatch(self._make_cmd(Cmd.DecreaseSubtitleDelay))

    def _running(self):
        return 1

    def _make_cmd(self, cmd_cls, *args, **kwargs):
        player_id = IdentityService.id_player()
        return super(PlayerMonitController, self)._make_cmd(
            cmd_cls, player_id, *args, **kwargs
        )
