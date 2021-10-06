""" Handlers for video commands """

from pathlib import Path

import structlog

from OpenCast.app.command import video as video_cmds
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.model.video import Video, timedelta
from OpenCast.infra.event.downloader import DownloadError, DownloadSuccess

from .service import Service


class VideoService(Service):
    def __init__(self, app_facade, service_factory, data_facade, media_factory):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, video_cmds)

        self._observe_event(PlayerEvt.PlayerStateUpdated)

        self._video_repo = data_facade.video_repo
        self._downloader = media_factory.make_downloader(app_facade.evt_dispatcher)
        self._source_service = service_factory.make_source_service(
            self._downloader, media_factory.make_video_parser()
        )
        self._subtitle_service = service_factory.make_subtitle_service(self._downloader)

    # Command handler implementation
    def _create_video(self, cmd):
        def impl(ctx, metadata):
            video = Video(cmd.model_id, cmd.source, cmd.collection_id, **metadata)
            ctx.add(video)

        if Path(cmd.source).is_file():
            metadata = self._source_service.pick_file_metadata(Path(cmd.source))
        else:
            metadata = self._source_service.pick_stream_metadata(cmd.source)

        if metadata is None:
            self._abort_operation(cmd.id, "Unavailable metadata", cmd=cmd)
            return

        if metadata["duration"]:
            metadata["duration"] = timedelta(seconds=metadata["duration"])

        self._start_transaction(self._video_repo, cmd.id, impl, metadata)

    def _delete_video(self, cmd):
        def impl(ctx):
            video = self._video_repo.get(cmd.model_id)
            video.delete()
            ctx.delete(video)

        self._start_transaction(self._video_repo, cmd.id, impl)

    def _retrieve_video(self, cmd):
        def impl(ctx, video):
            video.state = VideoState.COLLECTING

            # Video source is a filesystem path
            if video.from_disk():
                video.location = video.source
                ctx.update(video)
                return

            # Video source points to a stream
            if video.streamable():
                link = self._source_service.fetch_stream_link(video.source)
                if link is None:
                    self._abort_operation(cmd.id, "Unavailable stream URL", cmd=cmd)
                    return

                video.location = link
                ctx.update(video)
                return

            ctx.update(video)
            video_location = str(Path(cmd.output_directory) / f"{video.title}.mp4")

            # Video source points downloadable media
            def video_downloaded(_):
                def impl(ctx):
                    video.location = video_location
                    ctx.update(video)

                self._start_transaction(self._video_repo, cmd.id, impl)

            def abort_operation(evt):
                self._abort_operation(cmd.id, evt.error, cmd=cmd)

            self._evt_dispatcher.observe_result(
                cmd.id,
                {DownloadSuccess: video_downloaded, DownloadError: abort_operation},
                times=1,
            )
            self._downloader.download_video(
                cmd.id, video.id, video.source, video_location
            )

        video = self._video_repo.get(cmd.model_id)
        self._start_transaction(self._video_repo, cmd.id, impl, video)

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

    # Event handler implementation

    def start_video(self, ctx, video_id):
        video = self._video_repo.get(video_id)
        video.start()
        ctx.update(video)

    def stop_video(self, ctx, video_id):
        video = self._video_repo.get(video_id)
        video.stop()
        ctx.update(video)

    def _player_state_updated(self, evt):
        if evt.new == PlayerState.PLAYING:
            self._start_transaction(
                self._video_repo,
                evt.id,
                lambda ctx: self.start_video(ctx, evt.video_id),
            )
        elif evt.old == PlayerState.PLAYING:
            self._start_transaction(
                self._video_repo, evt.id, lambda ctx: self.stop_video(ctx, evt.video_id)
            )
