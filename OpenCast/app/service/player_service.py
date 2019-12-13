import logging
import uuid

from OpenCast.config import config
from OpenCast.domain.model.video import Video
from OpenCast.infra.media import subtitle

from ..command import player_commands
from .service import Service

subConfig = config['Subtitle']
logger = logging.getLogger(__name__)


class PlayerService(Service):
    def __init__(self, cmd_dispatcher, player, downloader):
        super(PlayerService,
              self).__init__(cmd_dispatcher, logger, self, player_commands)
        self._downloader = downloader
        self._player = player

    # Command handler interface implementation

    def _play_video(self, cmd):
        logger.debug("[controller] stream video, URL='{}'".format(cmd.source))
        self._player.stop(stop_browsing=True)

        video = Video(cmd.source)
        if video.from_disk():
            video.subtitle = subtitle.load_from_video(video, subConfig.language)
            self._player.play(video)
            return

        self._queue_video_impl(video, self._play_video_impl, first=True)

    def _queue_video(self, cmd):
        logger.debug("[controller] queue video, URL='{}'".format(cmd.source))

        video = Video(cmd.source)
        if video.from_disk():
            video.subtitle = subtitle.load_from_video(video, subConfig.language)
            self._player.queue(video)
            return

        self._queue_video_impl(video, self._player.queue, first=False)

    def _stop_video(self, cmd):
        logger.debug("[controller] stop current video")
        self._player.stop()

    def _toggle_video_state(self, cmd):
        self._player.play_pause()

    def _seek_video(self, cmd):
        logger.debug(
            "[controller] seek video time, duration={}".format(cmd.duration)
        )
        self._player.seek(cmd.duration)

    def _increase_volume(self, cmd):
        self._player.change_volume(cmd.amount)
        logger.debug(
            "[controller] change player volume, amount: {}".format(cmd.amount)
        )

    def _decrease_volume(self, cmd):
        self._player.change_volume(-cmd.amount)
        logger.debug(
            "[controller] change player volume, amount: {}".format(cmd.amount)
        )

    def _next_video(self, cmd):
        logger.debug("[controller] next video")
        self._player.next()

    def _prev_video(self, cmd):
        logger.debug("[controller] prev video")
        self._player.prev()

    def _toggle_subtitle(self, cmd):
        self._player.toggle_subtitle()

    def _increase_subtitle_delay(self, cmd):
        self._player.increase_subtitle_delay()

    def _decrease_subtitle_delay(self, cmd):
        self._player.decrease_subtitle_delay()

    # Private

    def _play_video_impl(self, video):
        self._player.queue(video, first=True)
        self._player.play()

    def _queue_video_impl(self, video, dl_callback, first):
        if '/playlist' in video.source:
            logger.debug("[controller] playlist detected, unfolding...")
            # Generate a unique ID for the playlist
            playlist_id = uuid.uuid4()
            urls = self._downloader.extract_playlist(video.source)
            videos = [Video(u, playlist_id) for u in urls]
            logger.debug(
                "[controller] playlist url unfolded to {}".format(videos)
            )
            self._downloader.queue(videos, dl_callback, first)
        else:
            logger.debug("[controller] queue single video: {}".format(video))
            self._downloader.queue([video], dl_callback, first)
