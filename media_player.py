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

        self.cv = threading.Condition()
        self.volume_ = default_volume
        self._make_fifo()
        self.state = PlayerState.stopped
        self.player = None
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

    def volume(self):
        return self.volume_

    # Omx player calls

    def stop(self):
        self.state = PlayerState.stopped
        self._stop_video()

    def next(self):
        self._stop_video()        
        self.play()

    def _stop_video(self):
        os.system("echo -n q > /tmp/cmd &")

    def start(self):
        os.system("echo -n . > /tmp/cmd &")

    def pause(self):
        os.system("echo -n p > /tmp/cmd &")

    def show_subtitles(self, show):
        if show:
            os.system("echo -n w > /tmp/cmd &")
        else:
            os.system("echo -n x > /tmp/cmd &")

    def change_volume(self, increase):
        if increase:
            os.system("echo -n + > /tmp/cmd &")
            self._set_volume(self.volume() + 300)
        else:
            os.system("echo -n - > /tmp/cmd &")
            self._set_volume(self.volume() - 300)

    def seek(self, forward, long):
        if forward:
            if long:    # Up arrow
                os.system("echo -n $'\x1b\x5b\x41' > /tmp/cmd &")
            else:       # Right arrow
                os.system("echo -n $'\x1b\x5b\x43' > /tmp/cmd &")
        else:
            if long:    # Down arrow
                os.system("echo -n $'\x1b\x5b\x42' > /tmp/cmd &")
            else:       # Left arrow
                os.system("echo -n $'\x1b\x5b\x44' > /tmp/cmd &")

    def play(self, video=None):
        with self.cv:
            if video is not None:
                self.queue.appendleft(video)
            self.state = PlayerState.ready
            self.cv.notify()

    def _play(self):
        self.state = PlayerState.playing
        video = self.queue.popleft()
        logger.info("Playing: %r" % (video))
        if self.player is None:
            self.player = OMXPlayer(video['path'], dbus_name=
                                    'org.mpris.MediaPlayer2.omxplayer1')
            logger.debug("LEAVE AFTER STARTING VIDEO")
        else:
            self.player.load(video['path'])

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
                    # Check every seconds that the process is still alive
                    self.cv.wait(1)
                    self._check_status()
                if self.stopped:
                    return

                self._play()

    def _set_volume(self, volume):
        self.volume_ = volume

    def _make_fifo(self):
        try:
            os.mkfifo("/tmp/cmd")
        except OSError as e:
            # 17 means the file already exists.
            if e.errno != 17:
                raise


def make_player(default_volume):
    omx_player = OmxPlayer(default_volume)

    return omx_player
