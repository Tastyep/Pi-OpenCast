import logging
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from pathlib import Path

import psutil

from omxplayer import keys
from omxplayer.player import OMXPlayer

from .config import config
from .history import History

logger = logging.getLogger(__name__)
config = config['VideoPlayer']


class PlayerState(Enum):
    INIT = 1
    READY = 2
    STARTED = 3
    STOPED = 4


# OmxPlayer documentation: https://elinux.org/Omxplayer
class PlayerWrapper(object):
    def __init__(self, player_factory):
        self._stopped = False
        self._queue = deque()
        self._history = History(items=[])

        self._volume = 1.0
        self._show_subtitle = True

        self._player = None
        self._player_factory = player_factory
        self._play_next = False
        self._state = PlayerState.INIT
        self._player_cv = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=1)

        self._player_cv = threading.Condition()
        self._video_player_thread = threading.Thread(target=self._play_videos)
        self._video_player_thread.start()

        def is_ready():
            with self._player_cv:
                return self._state is PlayerState.READY

        if not self._sync(5000, 500, is_ready):
            logger.error("[player] cannot initialize")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._stopped = True
        if self.playing():
            self.stop()
        else:
            self._notify_player()
        self._video_player_thread.join()

    def play(self, video=None):
        self._executor.submit(self._play_impl, video)

    def _play_impl(self, video=None):
        self._play_next = True
        if video is not None:
            self._history.stop_browsing()
            self._queue_impl(video, first=True)
            return

        self._notify_player()

    def queue(self, video, first=False):
        self._executor.submit(self._queue_impl, video, first)

    def _queue_impl(self, video, first=False):
        logger.info("[player] queue video: {}".format(video))
        # Position the video with the videos of the same playlist.
        index = 0 if first else len(self._queue)
        if first and video.playlist_id is not None:
            for i, v in enumerate(reversed(self._queue)):
                if v.playlist_id == video.playlist_id:
                    index = len(self._queue) - i
                    break
        self._queue.insert(index, video)
        logger.debug("[player] queue contains: {}".format(self._queue))
        self._notify_player()

    def list_queue(self):
        return list(self._queue)

    def stop(self, stop_browsing=False):
        self._executor.submit(self._stop_impl, stop_browsing)

    def _stop_impl(self, stop_browsing=False):
        if not self.playing():
            logger.debug("[player] is already stopped")
            return

        if stop_browsing is True:
            self._history.stop_browsing()

        logger.info("[player] stopping ...")
        self._play_next = False
        self._exec_command('stop')

        def is_stopped():
            return not self.playing()

        if not self._sync(5000, 500, is_stopped):
            logger.error("[player] cannot stop")

    def prev(self):
        self._executor.submit(self._prev_impl)

    def _prev_impl(self):
        if not self._history.can_prev():
            return

        if self.playing():
            self._stop_impl()
            self._prev_impl()

        self._history.prev()
        self._play_impl()

    def next(self):
        self._executor.submit(self._next_impl)

    def _next_impl(self):
        if self.playing():
            self._stop_impl()
        self._play_impl()

    def play_pause(self):
        def impl():
            if not self.playing():
                self._play_impl()
            else:
                self._exec_command('play_pause')

        self._executor.submit(impl)

    def toggle_subtitle(self):
        def impl():
            self._show_subtitle = not self._show_subtitle
            if self._show_subtitle:
                self._exec_command('show_subtitles')
            else:
                self._exec_command('hide_subtitles')

        self._executor.submit(impl)

    def increase_subtitle_delay(self):
        self._exec_command('action', keys.INCREASE_SUBTITLE_DELAY)

    def decrease_subtitle_delay(self):
        self._exec_command('action', keys.DECREASE_SUBTITLE_DELAY)

    def change_volume(self, increase):
        def impl():
            volume = self._volume
            if increase:
                volume += 0.1
            else:
                volume -= 0.1
            volume = max(min(2, volume), 0)
            if self._exec_command('set_volume', volume):
                self._volume = volume

        self._executor.submit(impl)

    def seek(self, forward, long):
        if forward:
            if long:  # Up arrow, + 5 minutes
                self._exec_command('seek', 300)
            else:  # Right arrow, + 30 seconds
                self._exec_command('seek', 30)
        else:
            if long:  # Down arrow, - 5 minutees
                self._exec_command('seek', -300)
            else:  # Left arrow, - 30 seconds
                self._exec_command('seek', -30)

    def playing(self):
        return self._state is PlayerState.STARTED

    def _notify_player(self):
        with self._player_cv:
            self._player_cv.notify()

    def _sync(self, timeout, interval, condition):
        step = round(timeout / interval)
        for i in range(step):
            if condition():
                return True
            time.sleep(interval / 1000.0)
        return False

    def _make_player(self, video):
        command = ['--vol', str(100 * (self._volume - 1.0))]

        if config.hide_background is True:
            command += ['--blank']

        if video.subtitle is not None:
            command += ['--subtitles', video.subtitle]

        for tries in range(5):
            logger.debug(
                "[player] opening {} with opt: {}".format(video, command)
            )
            try:
                self._player = self._player_factory(
                    video.path, command, 'org.mpris.MediaPlayer2.omxplayer1',
                    self._on_exit
                )
                return True
            except SystemError:
                logger.error("[player] couldn't connect to dbus")
            # Kill instance if it is a dbus problem
            for proc in psutil.process_iter():
                if "omxplayer" in proc.name():
                    logger.debug(
                        "[player] killing process {}".format(proc.name())
                    )
                    proc.kill()

        return False

    def _play(self):
        with self._player_cv:
            video = None
            if not self._history.browsing() and len(self._queue) == 0:
                self._prev_impl()

            if self._history.browsing():
                logger.debug(
                    "[player] picking video from history at index ({})".format(
                        self._history.index()
                    )
                )
                video = self._history.current_item()
                self._history.next()
            else:
                video = self._queue.popleft()
                self._history.push(video)

            if not video.path.is_file():
                logger.error("[player] file not found: {}".format(video))
                if self._history.browsing():
                    logger.error("[player] removing video")
                    self._history.remove(video)
                    self._history.stop_browsing()
                return

            if self._make_player(video):
                self._state = PlayerState.STARTED
                logger.info("[player] started")
            else:
                logger.error("[player] couldn't start")
                self._history.remove(video)

    def _play_videos(self):
        def should_play():
            def impl():
                logger.debug(
                    "[player] should_play: playing: {}, play_next: {}, qSize: {}, browsing: {}, loop {}, hSize: {}"
                    .format(
                        self.playing(), self._play_next, len(self._queue),
                        self._history.browsing(), config.loop_last,
                        self._history.size()
                    )
                )
                return (
                    self._stopped or (
                        not self.playing() and self._play_next and (
                            len(self._queue) > 0 or self._history.browsing() or
                            (config.loop_last and self._history.size() > 0)
                        )
                    )
                )

            logger.debug("[player] should_play()")
            f = self._executor.submit(impl)
            self._player_cv.release()
            result = f.result()
            self._player_cv.acquire()

            return result

        while (True):
            with self._player_cv:
                if self._state is PlayerState.INIT:
                    self._state = PlayerState.READY
                while not should_play():
                    self._player_cv.wait()

                if self._stopped:
                    return
            self._executor.submit(self._play).result()

    def _exec_command(self, command, *args, **kwargs):
        with self._player_cv:
            if not self.playing():
                return False
            logger.debug("[player] executing command {}".format(command))
            getattr(self._player, command)(*args, **kwargs)
            return True

    def _on_exit(self, player, code):
        with self._player_cv:
            logger.info("[player] stopped")
            self._player = None
            self._state = PlayerState.STOPED
            self._player_cv.notify()


def player_factory():
    def make_player(path, command, dbus_name, exit_callback):
        player = OMXPlayer(Path(path), command, dbus_name=dbus_name)

        player.exitEvent += exit_callback
        return player

    return make_player


def make_wrapper():
    return PlayerWrapper(player_factory())
