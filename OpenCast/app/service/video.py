from functools import partial
from pathlib import Path

import structlog
from OpenCast.app.command import video as video_cmds
from OpenCast.config import config
from OpenCast.domain.model.video import Video

from .service import Service


class VideoService(Service):
    def __init__(self, app_facade, data_facade, io_facade, service_factory):
        logger = structlog.get_logger(__name__)
        super(VideoService, self).__init__(app_facade, logger, self, video_cmds)
        self._video_repo = data_facade.video_repo()
        self._downloader = io_facade.video_downloader()
        self._source_service = service_factory.make_source_service(self._downloader)
        self._subtitle_service = service_factory.make_subtitle_service(
            io_facade.ffmpeg_wrapper()
        )

    # Command handler interface implementation
    def _create_video(self, cmd):
        def impl(ctx):
            video = Video(cmd.model_id, cmd.source, cmd.playlist_id)
            ctx.add(video)

        self._start_transaction(self._video_repo, cmd.id, impl)

    def _identify_video(self, cmd):
        def impl(ctx, video, metadata):
            video.title = metadata["title"]
            ctx.update(video)

        video = self._video_repo.get(cmd.model_id)
        metadata = self._source_service.fetch_metadata(video)
        if metadata is None:
            self._abort_operation(cmd, "can't fetch metadata")
            return

        self._start_transaction(self._video_repo, cmd.id, impl, video, metadata)

    def _retrieve_video(self, cmd):
        def impl(ctx, video):
            video.path = Path(video.source)
            ctx.update(video)

        video = self._video_repo.get(cmd.model_id)
        if video.is_file():
            self._start_transaction(self._video_repo, cmd.id, impl, video)
            return

        def video_downloaded(ctx, data):
            video = self._video_repo.get(data.id)
            video.path = data.path
            ctx.update(video)

        output_dir = config["downloader.output_directory"]
        video.path = Path(f"{output_dir}/{video.title}.mp4")
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
