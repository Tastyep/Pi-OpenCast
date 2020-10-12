""" Handlers for video commands """

from pathlib import Path

import structlog

from OpenCast.app.command import video as video_cmds
from OpenCast.domain.model.video import Video
from OpenCast.infra.event.downloader import DownloadError, DownloadSuccess

from .service import Service


class VideoService(Service):
    def __init__(self, app_facade, service_factory, data_facade, media_factory):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, self, video_cmds)
        self._video_repo = data_facade.video_repo
        self._downloader = media_factory.make_downloader(app_facade.evt_dispatcher)
        self._source_service = service_factory.make_source_service(
            self._downloader, media_factory.make_video_parser()
        )
        self._subtitle_service = service_factory.make_subtitle_service(self._downloader)

    # Command handler implementation
    def _create_video(self, cmd):
        def impl(ctx, metadata):
            video = Video(cmd.model_id, cmd.source, **metadata)
            ctx.add(video)

        if Path(cmd.source).is_file():
            metadata = self._source_service.pick_file_metadata(Path(cmd.source))
        else:
            metadata = self._source_service.pick_stream_metadata(cmd.source)

        if metadata is None:
            self._abort_operation(cmd.id, "Can't fetch metadata")
            return

        self._start_transaction(self._video_repo, cmd.id, impl, metadata)

    def _delete_video(self, cmd):
        def impl(ctx):
            video = self._video_repo.get(cmd.model_id)
            video.delete()
            ctx.delete(video)

        self._start_transaction(self._video_repo, cmd.id, impl)

    def _retrieve_video(self, cmd):
        def impl(ctx, video):
            video.path = Path(video.source)
            ctx.update(video)

        video = self._video_repo.get(cmd.model_id)
        if video.from_disk():
            self._start_transaction(self._video_repo, cmd.id, impl, video)
            return

        def video_downloaded(_):
            def impl(ctx):
                ctx.update(video)

            self._start_transaction(self._video_repo, cmd.id, impl)

        def abort_operation(evt):
            self._abort_operation(cmd.id, evt.error)

        video.path = Path(cmd.output_directory) / f"{video.title}.mp4"
        self._evt_dispatcher.observe_result(
            cmd.id,
            {DownloadSuccess: video_downloaded, DownloadError: abort_operation},
            times=1,
        )
        self._downloader.download_video(cmd.id, video.source, str(video.path))

    def _parse_video(self, cmd):
        def impl(ctx):
            video = self._video_repo.get(cmd.model_id)
            streams = self._source_service.list_streams(video)
            video.streams = streams
            ctx.update(video)

        self._start_transaction(self._video_repo, cmd.id, impl)

    def _fetch_video_subtitle(self, cmd):
        def impl(ctx):
            video = self._video_repo.get(cmd.model_id)
            video.subtitle = self._subtitle_service.fetch_subtitle(video, cmd.language)
            ctx.update(video)

        self._start_transaction(self._video_repo, cmd.id, impl)
