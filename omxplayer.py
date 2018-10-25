import os
import threading

from collections import deque
from enum import Enum


# Video player status enumeration
class PlayerState(Enum):
    stopped = 1
    playing = 2


# OmxPlayer documentation: https://elinux.org/Omxplayer
class OmxPlayer(object):
    queue = deque()
    volume = 0
    state = PlayerState.stopped

    def queue_video(self, video):
        self.queue.append(video)

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

    def set_volume(self, volume):
        self.volume = volume

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

    def play(self, video):
        threading.Thread(target=self.__play, args=(video,)).start()

    def __play(self, video):
        self.state = PlayerState.playing
        os.system(
            "omxplayer -o both '" + video['path'] + "'"
            + " --vol " + str(self.volume)
            # + " --subtitles subtitle.srt < /tmp/cmd"
        )
        if self.state == PlayerState.playing:
            if len(self.queue) > 0:
                video = self.queue.popleft()
                self.play(video)
            else:
                self.stop()


def make_player():
    omx_player = OmxPlayer()

    return omx_player
