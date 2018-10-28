import os
import logging
import threading

from omxplayer.player import OMXPlayer, OMXPlayerDeadError
from dbus import DBusException
from collections import deque
from enum import Enum

logger = logging.getLogger("App")


# Video player status enumeration
class PlayerState(Enum):
    stopped = 0
    ready = 1
    playing = 2


# OmxPlayer documentation: https://elinux.org/Omxplayer
class OmxPlayer(object):
    def __init__(self, default_volume):
        self.stopped = False
        self.queue = deque()

        self.volume = default_volume
        self.state = PlayerState.stopped

        self.player = None
        self.cv = threading.Condition()
        self.monitor = threading.Thread(target=self._monitor)
        self.monitor.start()

    def __del__(self):
        with self.cv:
            self.stopped = True
            self.stop()

    def queue_video(self, video):
        with self.cv:
            logger.debug("Queue video: %r" % (video))
            self.queue.append(video)
            self.cv.notify()

    # Omx player calls

    def stop(self):
        with self.cv:
            self._exec_command('stop')
            self.state = PlayerState.stopped

    def next(self):
        self._exec_command('stop')
        self.play()

    def play_pause(self):
        with self.cv:
            if self.state is PlayerState.playing:
                self._exec_command('play_pause')
            else:
                self.play()

    def show_subtitles(self, show):
        if show:
            self._exec_command('show_subtitles')
        else:
            self._exec_command('hide_subtitles')

    def change_volume(self, increase):
        with self.cv:
            if increase:
                self.volume += 100
            else:
                self.volume -= 100
            self._exec_command('set_volume', self.volume)

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

    def play(self, video=None):
        with self.cv:
            if video is not None:
                self.queue.appendleft(video)
            self.state = PlayerState.ready
            self.cv.notify()

    def _play(self):
        video = self.queue.popleft()
        logger.info("Playing: %r" % (video))
        if self.player is None:
            self.player = OMXPlayer(video['path'],
                                    ['--vol', str(self.volume)],
                                    dbus_name=
                                    'org.mpris.MediaPlayer2.omxplayer1')
        else:
            self.player.load(video['path'])
            self.player.set_volume(self.volume)
        self.state = PlayerState.playing

    def _check_status(self):
        if self.state is PlayerState.playing:
            try:
                self.player.is_playing()
            except (OMXPlayerDeadError, DBusException):
                self.state = PlayerState.ready

    def _monitor(self):
        while (True):
            with self.cv:
                while (self.stopped is False
                       and (self.state is not PlayerState.ready
                            or len(self.queue) == 0)):
                    # Add wakup delay until the player wrapper library
                    # finally merges the onExit event.
                    self.cv.wait(1)
                    self._check_status()
                if self.stopped:
                    return

                self._play()

    def _exec_command(self, command, *args, **kwargs):
        with self.cv:
            if self.player is not None and self.state is PlayerState.playing:
                getattr(self.player, command)(*args, **kwargs)


def make_player(default_volume):
    omx_player = OmxPlayer(default_volume)

    return omx_player
