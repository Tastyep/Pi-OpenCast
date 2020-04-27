from threading import Lock

import psutil

import OpenCast.infra.event.player as e
import structlog
from omxplayer import keys
from OpenCast.config import config

from .error import PlayerError

config = config["VideoPlayer"]


# OmxPlayer documentation: https://elinux.org/Omxplayer
class PlayerWrapper:
    def __init__(self, evt_dispatcher, player_factory):
        self._logger = structlog.get_logger(__name__)
        self._evt_dispatcher = evt_dispatcher
        self._player_factory = player_factory
        self._player = None
        self._player_lock = Lock()
        self._stop_operation_id = None

    def play(self, cmd_id, video, volume):
        command = ["--vol", self._downscale(volume)]
        if config.hide_background is True:
            command += ["--blank"]

        if video.subtitle is not None:
            command += ["--subtitles", video.subtitle]

        def open_player():
            self._logger.debug("Opening video", video=video, opt=command)
            try:
                self._player = self._player_factory(
                    video.path,
                    command,
                    "org.mpris.MediaPlayer2.omxplayer1",
                    self._on_exit,
                )
                return True
            except SystemError:
                self._logger.error("Dbus error", error="Couldn't connect")
                # Kill instance if it is a dbus problem
                for proc in psutil.process_iter():
                    if "omxplayer" in proc.name():
                        self._logger.debug(f"Killing process", process=proc.name())
                        proc.kill()
                return False

        with self._player_lock:
            for _ in range(5):
                if open_player():
                    self._dispatch(e.PlayerStarted(cmd_id, video))
                    return
        raise PlayerError("error starting the player")

    def stop(self, cmd_id):
        def impl():
            self._stop_operation_id = cmd_id
            self._player.stop()
            # Event is dispatched from _on_exit

        self._exec_command(impl)

    def pause(self, cmd_id):
        def impl():
            self._player.play_pause()
            self._dispatch(e.PlayerPaused(cmd_id))

        self._exec_command(impl)

    def unpause(self, cmd_id):
        def impl():
            self._player.play_pause()
            self._dispatch(e.PlayerUnpaused(cmd_id))

        self._exec_command(impl)

    def update_subtitle_state(self, cmd_id, state):
        def impl():
            if state is True:
                self._player.show_subtitles()
            else:
                self._player.hide_subtitles()
            self._dispatch(e.SubtitleStateChanged(cmd_id, state))

        self._exec_command(impl)

    def increase_subtitle_delay(self, cmd_id):
        def impl():
            self._player.action(keys.INCREASE_SUBTITLE_DELAY)
            self._dispatch(e.SubtitleDelayUpdated(cmd_id, 250))

        self._exec_command(impl)

    def decrease_subtitle_delay(self, cmd_id):
        def impl():
            self._player.action(keys.DECREASE_SUBTITLE_DELAY)
            self._dispatch(e.SubtitleDelayUpdated(cmd_id, -250))

        self._exec_command(impl)

    def set_volume(self, cmd_id, volume):
        def impl():
            self._player.set_volume(self._downscale(volume))
            self._dispatch(e.VolumeUpdated(cmd_id, volume))

        self._exec_command(impl)

    def seek(self, cmd_id, duration):
        def impl():
            self._player.seek(duration)
            self._dispatch(e.VideoSeeked(cmd_id))

        self._exec_command(impl)

    def _downscale(self, volume):
        return volume / 100

    def _exec_command(self, command):
        with self._player_lock:
            if self._player is None:
                raise PlayerError("the player is not started")
            command()

    def _dispatch(self, event):
        self._evt_dispatcher.dispatch(event)

    def _on_exit(self, player, code):
        with self._player_lock:
            evt = e.PlayerStopped(self._stop_operation_id)
            self._stop_operation_id = None
            self._player = None
            self._dispatch(evt)
