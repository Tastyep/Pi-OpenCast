import logging
from functools import partial

from OpenCast.app.command import video as video_cmds
from OpenCast.domain.model.video import Video

from .service import Service


class VideoService(Service):
    def __init__(self, app_facade, data_facade, io_facade, service_factory):
        logger = logging.getLogger(__name__)
        super(VideoService, self).__init__(app_facade, logger, self, video_cmds)
        self._video_repo = data_facade.video_repo()
        self._downloader = io_facade.video_downloader()
        self._subtitle_service = service_factory.make_subtitle_service(
            io_facade.ffmpeg_wrapper()
        )

    # Command handler interface implementation
    def _add_video(self, cmd):
        def save_to_db(ctx, video):
            ctx.add(video)

        video = Video(cmd.model_id, cmd.source, cmd.playlist_id, cmd.title, cmd.path)
        self._start_transaction(self._video_repo, cmd.id, save_to_db, video)

    def _download_video(self, cmd):
        def video_downloaded(ctx, data):
            video = self._video_repo.get(data.id)
            video.downloaded()
            ctx.update(video)

        video = self._video_repo.get(cmd.model_id)
        callback = partial(
            self._start_transaction, self._video_repo, cmd.id, video_downloaded
        )
        self._downloader.queue(video, callback, priority=cmd.priority)

    def _fetch_video_subtitle(self, cmd):
        def impl(ctx):
            video = self._video_repo.get(cmd.model_id)
            video.subtitle = self._subtitle_service.load_from_disk(video, cmd.language)
            ctx.update(video)

        self._start_transaction(self._video_repo, cmd.id, impl)
