import os
from threading import Thread, Condition

from collections import deque
from enum import Enum


# Video player status enumeration
class PlayerState(Enum):
    stopped = 0
    playing = 1


# OmxPlayer documentation: https://elinux.org/Omxplayer
class OmxPlayer(object):
    def __init__(self, default_volume):
        self.stopped = False
        self.queue = deque()

        self.volume = default_volume

        self.cv = Condition()
        self.thread = Thread(target=self.__play)
        self.thread.start()

    def __del__(self):
        with self.cv:
            self.stopped = True
            self.stop()
            self.cv.notifyAll()
        self.thread.join()

    def queue_video(self, video):
        with self.cv:
            self.queue.append(video)
            if self.state == PlayerState.playing:
                self.cv.notify()

    # Omx player calls

    def stop(self):
        self.state = PlayerState.stopped
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
            self.set_volume(self.volume + 300)
        else:
            os.system("echo -n - > /tmp/cmd &")
            self.set_volume(self.volume - 300)

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
            self.state = PlayerState.playing
            self.cv.notify()

    def __play(self):
        while not self.stopped:
            with self.cv:
                while not self.stopped and (len(self.queue) == 0 or
                                            self.state == PlayerState.stopped):
                    self.cv.wait()
                if self.stopped:
                    return

                video = self.queue.popleft()
            os.system(
                "omxplayer -o both '" + video['path'] + "'"
                + " --vol " + str(self.volume)
                # + " --subtitles subtitle.srt < /tmp/cmd"
            )


def make_player(default_volume):
    omx_player = OmxPlayer(default_volume)

    return omx_player
