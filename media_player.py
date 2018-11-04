import logging
import threading
import time

from omxplayer.player import OMXPlayer, OMXPlayerDeadError
from dbus import DBusException
from collections import deque
from enum import Enum
from functools import total_ordering

logger = logging.getLogger("App")


# Video player status enumeration
@total_ordering
class PlayerState(Enum):
    stopped = 1
    ready = 2
    paused = 3
    playing = 4

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
            logger.info("[player] Queue video: %r" % (video))
            # Position the video with the videos of the same playlist.
            index = 0 if first else len(self._queue)
            if first and video.playlistId is not None:
                for i, v in enumerate(reversed(self._queue)):
                    if v.playlistId == video.playlistId:
                        index = len(self._queue) - i
                        break
            self._queue.insert(index, video)
            logger.debug("player queue contains: %r" % (self._queue))
            self._cv.notify()

    def list_queue(self):
        return list(self._queue)

    def stop(self):
        with self._cv:
            self._exec_command('stop')
            logger.debug("Waiting for omxplayer to stop")
            while self._check_status() is True:
                time.sleep(1)
            logger.debug("omxplayer stopped")
            self._state = PlayerState.stopped

    def next(self):
        self.stop()
        self.play()

    def play_pause(self):
        self._exec_command('play_pause')

    def show_subtitles(self, show):
        if show:
            self._exec_command('show_subtitles')
        else:
            self._exec_command('hide_subtitles')

    def change_volume(self, increase):
        with self._cv:
            if increase:
                self._volume += 100
            else:
                self._volume -= 100
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

    def _play(self):
        video = self._queue.popleft()
        logger.info("Playing: %r" % (video))

        command = ['--vol', str(self._volume)]
        for sub in video.subtitles:
            command += ['--subtitles', sub]

        self._player = OMXPlayer(video.path,
                                 command,
                                 dbus_name='org.mpris.MediaPlayer2.omxplayer1')
        # Wait for the DBus interface to be initialised
        logger.debug("Waiting for omxplayer start")
        self._state = PlayerState.playing
        while self._check_status() is False:
            time.sleep(1)
        logger.debug("omxplayer started")

    def _check_status(self):
        if self._state <= PlayerState.ready:
            return False
        try:
            if self._player.is_playing():
                self._state = PlayerState.playing
            else:
                self._state = PlayerState.paused
        except (OMXPlayerDeadError, DBusException):
            self._state = PlayerState.ready

        return self._state > PlayerState.ready

    def _monitor(self):
        while (True):
            with self._cv:
                while (self._stopped is False
                       and (self._state is not PlayerState.ready
                            or len(self._queue) == 0)):
                    # Add wakup delay until the player wrapper library
                    # finally merges the onExit event.
                    self._cv.wait(1)
                    self._check_status()
                if self._stopped:
                    return

                self._play()

    def _exec_command(self, command, *args, **kwargs):
        with self._cv:
            if self._player is not None and self._state > PlayerState.ready:
                getattr(self._player, command)(*args, **kwargs)


def make_player(default_volume):
    omx_player = OmxPlayer(default_volume)

    return omx_player
