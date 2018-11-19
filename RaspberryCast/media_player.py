import logging
import threading
import time

from omxplayer.player import OMXPlayer, OMXPlayerDeadError
from dbus import DBusException
from collections import deque
from enum import Enum
from functools import total_ordering

from .config import config
logger = logging.getLogger(__name__)


# Video player status enumeration
@total_ordering
class PlayerState(Enum):
    stopped = 0
    ready = 1
    playing = 2

    def __lt__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self.value < other.value


# OmxPlayer documentation: https://elinux.org/Omxplayer
class OmxPlayer(object):
    def __init__(self, default_volume):
        self._stopped = False
        self._queue = deque()

        self._volume = default_volume
        self._state = PlayerState.ready

        self._player = None
        self._cv = threading.Condition()
        self._monitor = threading.Thread(target=self._monitor)
        self._monitor.start()

    def __del__(self):
        with self._cv:
            self._stopped = True
            self.stop()

    @property
    def volume(self):
        return self._volume

    def play(self, video=None):
        with self._cv:
            if video is not None:
                self.queue(video, first=True)
            if self._state < PlayerState.ready:
                self._state = PlayerState.ready
            self._cv.notify()

    def queue(self, video, first=False):
        with self._cv:
            logger.info("[player] queue video: %r" % (video))
            # Position the video with the videos of the same playlist.
            index = 0 if first else len(self._queue)
            if first and video.playlistId is not None:
                for i, v in enumerate(reversed(self._queue)):
                    if v.playlistId == video.playlistId:
                        index = len(self._queue) - i
                        break
            self._queue.insert(index, video)
            logger.debug("[player] queue contains: %r" % (self._queue))
            self._cv.notify()

    def list_queue(self):
        return list(self._queue)

    def stop(self):
        with self._cv:
            if self._state is not PlayerState.playing:
                logger.debug("[player] is already stopped")
                return

            logger.debug("[player] stopping ...")
            self._exec_command('stop')
            self._state = PlayerState.ready
        if not self._sync(5000,
                          500,
                          self._wait_stopped):
            logger.error("[player] couldn't stop")

    def next(self):
        self.stop()
        self.play()

    def play_pause(self):
        with self._cv:
            self._exec_command('play_pause')
            if self._state == PlayerState.stopped:
                self.play()

    def show_subtitles(self, show):
        if show:
            self._exec_command('show_subtitles')
        else:
            self._exec_command('hide_subtitles')

    def change_volume(self, increase):
        with self._cv:
            if increase:
                self._volume += 0.1
            else:
                self._volume -= 0.1
            self._volume = max(min(2, self._volume), 0)
            self._exec_command('set_volume', self._volume)

    def seek(self, forward, long):
        if forward:
            if long:    # Up arrow, + 5 minutes
                self._exec_command('seek', 300)
            else:       # Right arrow, + 30 seconds
                self._exec_command('seek', 30)
        else:
            if long:    # Down arrow, - 5 minutees
                self._exec_command('seek', -300)
            else:       # Left arrow, - 30 seconds
                self._exec_command('seek', -30)

    def _sync(self, timeout, interval, condition):
        step = round(timeout / interval)
        for i in range(step):
            if condition():
                return True
            time.sleep(interval / 1000.0)
        return False

    def _wait_stopped(self):
        with self._cv:
            return self._state is PlayerState.stopped

    def _sync_with_bus(self):
        try:
            self._player.is_playing()
            return True
        except (OMXPlayerDeadError, DBusException):
            return False

    def _play(self):
        video = self._queue.popleft()
        logger.info("[player] playing: %r" % (video))

        command = ['--vol', str(100 * (self._volume - 1.0))]
        for sub in video.subtitles:
            command += ['--subtitles', sub]
        if config.hide_background is True:
            command += ['--blank']

        logger.debug("[player] starting player with opt: {}".format(command))
        self._player = OMXPlayer(video.path,
                                 command,
                                 dbus_name='org.mpris.MediaPlayer2.omxplayer1')
        self._player.exitEvent += self._on_exit
        self._state = PlayerState.playing

        # Wait for the DBus interface to be initialised
        if not self._sync(5000,
                          500,
                          self._sync_with_bus):
            logger.error("[player] couldn't connect to dbus")
        logger.debug("[player] started")

    def _monitor(self):
        while (True):
            with self._cv:
                while (self._stopped is False
                       and (self._state is not PlayerState.ready
                            or len(self._queue) == 0)):
                    self._cv.wait()
                if self._stopped:
                    return

                self._play()

    def _exec_command(self, command, *args, **kwargs):
        with self._cv:
            if self._player is not None and self._state > PlayerState.ready:
                getattr(self._player, command)(*args, **kwargs)

    def _on_exit(self, player, code):
        with self._cv:
            logger.debug("[player] stopped")

            if self._state is PlayerState.playing:
                logger.debug("[player] ready")
                self._state = PlayerState.ready
                self._cv.notify()
                return

            self._state = PlayerState.stopped


def make_player(default_volume):
    omx_player = OmxPlayer(default_volume)

    return omx_player
