import logging
from threading import Lock

import psutil

import OpenCast.infra.event.player_events as e
from omxplayer import keys
from OpenCast.config import config

from .error import PlayerError

logger = logging.getLogger(__name__)
config = config["VideoPlayer"]


# OmxPlayer documentation: https://elinux.org/Omxplayer
class PlayerWrapper:
    def __init__(self, evt_dispatcher, player_factory):
        self._evt_dispatcher = evt_dispatcher
        self._player_factory = player_factory
        self._player = None
        self._player_lock = Lock()
        self._interrupted = False

    def play(self, video, volume):
        command = ["--vol", self._downscale(volume)]
        if config.hide_background is True:
            command += ["--blank"]

        if video.subtitle is not None:
            command += ["--subtitles", video.subtitle]

        def open_player():
            logger.debug(f"opening {video} with opt: {command}")
            try:
                self._player = self._player_factory(
                    video.path,
                    command,
                    "org.mpris.MediaPlayer2.omxplayer1",
                    self._on_exit,
                )
                return True
            except SystemError:
                logger.error(f"couldn't connect to dbus")
                # Kill instance if it is a dbus problem
                for proc in psutil.process_iter():
                    if "omxplayer" in proc.name():
                        logger.debug(f"killing process {proc.name()}")
                        proc.kill()
                return False

        with self._player_lock:
            for _ in range(5):
                if open_player():
                    self._dispatch(e.PlayerStarted(video))
                    return
        raise PlayerError("could not start the player, check your logs")

    def stop(self):
        def impl():
            self._interrupted = True
            self._player.stop()
            # Event is dispatched from _on_exit

        self._exec_command(impl)

    def pause(self):
        def impl():
            self._player.play_pause()
            self._dispatch(e.PlayerPaused())

        self._exec_command(impl)

    def unpause(self):
        def impl():
            self._player.play_pause()
            self._dispatch(e.PlayerUnpaused())

        self._exec_command(impl)

    def update_subtitle_state(self, state):
        def impl():
            if state is True:
                self._player.show_subtitles()
            else:
                self._player.hide_subtitles()
            self._dispatch(e.SubtitleStateChanged(state))

        self._exec_command(impl)

    def increase_subtitle_delay(self):
        def impl():
            self._player.action(keys.INCREASE_SUBTITLE_DELAY)
            self._dispatch(e.SubtitleDelayUpdated(250))

        self._exec_command(impl)

    def decrease_subtitle_delay(self):
        def impl():
            self._player.action(keys.DECREASE_SUBTITLE_DELAY)
            self._dispatch(e.SubtitleDelayUpdated(-250))

        self._exec_command(impl)

    def set_volume(self, volume):
        def impl():
            self._player.set_volume(self._downscale(volume))
            self._dispatch(e.VolumeUpdated(volume))

        self._exec_command(impl)

    def seek(self, duration):
        def impl():
            self._player.seek(duration)
            self._dispatch(e.VideoSeeked())

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
        cmd = None
        with self._player_lock:
            cmd = e.PlayerStopped(self._interrupted)
            self._interrupted = False
            self._player = None
        self._dispatch(cmd)
