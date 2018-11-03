import logging
import threading
import time

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

    def queue(self, video, first=False):
        with self._cv:
            logger.debug("[player] Queue video: %r" % (video))
            if first:
                # Position the video with the videos of the same playlist.
                if video.playlistId is not None:
                    videos = list(self._queue)
                    index = 0
                    for i, v in enumerate(reversed(videos)):
                        if v.playlistId == video.playlistId:
                            index = len(videos) - i
                            break
                    if index is 0:
                        self._queue.appendleft(video)
                    else:
                        videos.insert(index, video)
                        self._queue = deque(videos)
                else:
                    self._queue.appendleft(video)
            else:
                self._queue.append(video)
            logger.debug("player queue contains:")
            for v in self._queue:
                logger.debug(v)
            self._cv.notify()

    def list_queue(self):
        return list(self._queue)

    # Omx player calls

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
        with self._cv:
            if self._state is PlayerState.playing:
                self._exec_command('play_pause')
            else:
                self.play()

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

    def play(self, video=None):
        with self._cv:
            if video is not None:
                self._queue.appendleft(video)
            self._state = PlayerState.ready
            self._cv.notify()

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
        while self._check_status() is False:
            time.sleep(1)
        logger.debug("omxplayer started")
        self._state = PlayerState.playing

    def _check_status(self):
        if self._state is PlayerState.playing:
            try:
                return self._player.is_playing()
            except (OMXPlayerDeadError, DBusException):
                self._state = PlayerState.ready
                return False

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
            if self._player is not None and self._state is PlayerState.playing:
                getattr(self._player, command)(*args, **kwargs)


def make_player(default_volume):
    omx_player = OmxPlayer(default_volume)

    return omx_player
