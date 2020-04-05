import uuid

from bottle import request
from OpenCast.domain.model.player import Player

from ..command import player_commands as c
from .controller import Controller


class PlayerMonitController(Controller):
    def __init__(self, app_facade, data_facade, io_facade):
        super(PlayerMonitController, self).__init__(app_facade)

        self._player_repo = data_facade.player_repo()
        self._player_repo.create(Player(uuid.uuid4()))
        self._video_repo = data_facade.video_repo()

        # TODO add video monit controller
        server = io_facade.server()
        server.route("/stream", callback=self._stream)
        server.route("/queue", callback=self._queue)
        server.route("/video", callback=self._video)
        server.route("/subtitle", callback=self._subtitle)
        server.route("/sound", callback=self._sound)
        server.route("/running", callback=self._running)

    def _stream(self):
        cmd = c.PlayVideo(request.query["url"])
        self._cmd_dispatcher.dispatch(cmd)
        return "1"

    def _queue(self):
        cmd = c.QueueVideo(request.query["url"])
        self._cmd_dispatcher.dispatch(cmd)

    def _video(self):
        control = request.query["control"]
        cmd = None

        if control == "pause":
            cmd = c.ToggleVideoState()
        elif control == "stop":
            cmd = c.StopVideo()
        elif control == "right":
            cmd = c.SeekVideo(30)
        elif control == "left":
            cmd = c.SeekVideo(-30)
        elif control == "longright":
            cmd = c.SeekVideo(300)
        elif control == "longleft":
            cmd = c.SeekVideo(-300)
        elif control == "prev":
            cmd = c.PrevVideo()
        elif control == "next":
            cmd = c.NextVideo()
        else:
            return "0"

        self._cmd_dispatcher.dispatch(cmd)
        return "1"

    def _sound(self):
        cmd = None
        if request.query["vol"] == "more":
            cmd = c.ChangeVolume(10)
        else:
            cmd = c.ChangeVolume(-10)

        self._cmd_dispatcher.dispatch(cmd)
        return "1"

    def _subtitle(self):
        action = request.query["action"]

        if action == "toggle":
            self._cmd_dispatcher.dispatch(c.ToggleSubtitle())
        elif action == "increase":
            self._cmd_dispatcher.dispatch(c.IncreaseSubtitleDelay())
        elif action == "decrease":
            self._cmd_dispatcher.dispatch(c.DecreaseSubtitleDelay())

    def _running(self):
        return 1
