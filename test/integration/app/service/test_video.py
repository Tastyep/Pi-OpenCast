from pathlib import Path
from unittest.mock import MagicMock, Mock

from OpenCast.app.command import video as Cmd
from OpenCast.app.service.error import OperationError
from OpenCast.app.service.video import VideoService
from OpenCast.config import config
from OpenCast.domain.event import video as Evt
from OpenCast.domain.model.video import Stream, Video
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.event.downloader import DownloadError, DownloadSuccess

from .util import ServiceTestCase


class VideoServiceTest(ServiceTestCase):
    def setUp(self):
        super(VideoServiceTest, self).setUp()

        self.downloader = Mock()
        self.video_parser = Mock()
        self.media_factory = self.infra_facade.media_factory
        self.media_factory.make_downloader.return_value = self.downloader
        self.media_factory.make_video_parser.return_value = self.video_parser

        self.service = VideoService(
            self.app_facade, self.service_factory, self.data_facade, self.media_factory
        )

        self.video_repo = self.data_facade.video_repo

    def test_create_video(self):
        source = "source"
        playlist_id = IdentityService.id_playlist(source)
        video_id = IdentityService.id_video(source)
        video = Video(video_id, source, playlist_id)

        self.evt_expecter.expect(
            Evt.VideoCreated, video.source, video.playlist_id
        ).from_(Cmd.CreateVideo, video.id, video.source, video.playlist_id)

    def test_delete_video(self):
        self.data_producer.video("source", None).video("source2", None).populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoDeleted).from_(Cmd.DeleteVideo, video_id)

        other_video_id = IdentityService.id_video("source2")
        self.assertListEqual(
            [self.video_repo.get(other_video_id)], self.video_repo.list()
        )

    def test_identify_video(self):
        self.data_producer.video("source", None).populate(self.data_facade)

        metadata = {"title": "title", "thumbnail": "thumbnail_url"}
        self.downloader.pick_stream_metadata.return_value = metadata

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoIdentified, metadata).from_(
            Cmd.IdentifyVideo, video_id
        )

    def test_retrieve_video_success(self):
        video_id = IdentityService.id_video("source")
        video_title = "video_title"
        self.data_producer.video(
            "source", None, metadata={"title": video_title}
        ).populate(self.data_facade)

        def dispatch_downloaded(op_id, *args):
            self.app_facade.evt_dispatcher.dispatch(DownloadSuccess(op_id))

        self.downloader.download_video.side_effect = dispatch_downloaded
        output_dir = config["downloader.output_directory"]
        path = Path(output_dir) / f"{video_title}.mp4"
        self.evt_expecter.expect(Evt.VideoRetrieved, path).from_(
            Cmd.RetrieveVideo, video_id, output_dir
        )

    def test_retrieve_video_error(self):
        video_id = IdentityService.id_video("source")
        video_title = "video_title"
        self.data_producer.video(
            "source", None, metadata={"title": video_title}
        ).populate(self.data_facade)

        def dispatch_error(op_id, *args):
            self.app_facade.evt_dispatcher.dispatch(
                DownloadError(op_id, "Download error")
            )

        self.downloader.download_video.side_effect = dispatch_error
        output_dir = config["downloader.output_directory"]
        self.evt_expecter.expect(OperationError, "Download error").from_(
            Cmd.RetrieveVideo, video_id, output_dir
        )

    def test_parse_video(self):
        self.data_producer.video("source", None, path=Path("/tmp/source.mp4")).populate(
            self.data_facade
        )

        streams = [
            (0, "video", None),
            (1, "audio", None),
            (2, "subtitle", "subtitle_lang"),
        ]
        self.video_parser.parse_streams.return_value = streams

        expected = [Stream(*stream) for stream in streams]
        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoParsed, expected).from_(
            Cmd.ParseVideo, video_id
        )

    def test_fetch_video_subtitle(self):
        path_mock = MagicMock()
        self.data_producer.video("source", None, path=path_mock).populate(
            self.data_facade
        )

        # Load from disk
        disk_subtitle = "/tmp/source.srt"
        path_mock.with_suffix.return_value = disk_subtitle
        parent_mock = Mock()
        path_mock.parents.__getitem__.return_value = parent_mock
        parent_mock.glob.return_value = []

        # Download from source
        source_subtitle = "/tmp/source.vtt"
        self.downloader.download_subtitle.return_value = source_subtitle

        video_id = IdentityService.id_video("source")
        subtitle_language = config["subtitle.language"]
        self.evt_expecter.expect(Evt.VideoSubtitleFetched, Path(source_subtitle)).from_(
            Cmd.FetchVideoSubtitle, video_id, subtitle_language
        )
