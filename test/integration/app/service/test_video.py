from pathlib import Path
from unittest.mock import Mock

from OpenCast.app.command import video as Cmd
from OpenCast.app.service.error import OperationError
from OpenCast.app.service.video import VideoService
from OpenCast.config import config
from OpenCast.domain.event import video as Evt
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.event.downloader import DownloadError, DownloadSuccess

from .util import ServiceTestCase


class VideoServiceTest(ServiceTestCase):
    def setUp(self):
        super(VideoServiceTest, self).setUp()

        self.downloader = Mock()
        self.ffmpeg_wrapper = Mock()
        self.io_factory = self.infra_facade.io_factory
        self.io_factory.make_downloader.return_value = self.downloader
        self.io_factory.make_ffmpeg_wrapper.return_value = self.ffmpeg_wrapper

        self.service = VideoService(
            self.app_facade, self.service_factory, self.data_facade, self.io_factory
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

        title = "video_title"
        self.downloader.pick_stream_metadata.return_value = {"title": title}

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoIdentified, title).from_(
            Cmd.IdentifyVideo, video_id
        )

    def test_retrieve_video_success(self):
        video_id = IdentityService.id_video("source")
        video_title = "video_title"
        self.data_producer.video("source", None, title=video_title).populate(
            self.data_facade
        )

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
        self.data_producer.video("source", None, title=video_title).populate(
            self.data_facade
        )

        def dispatch_error(op_id, *args):
            self.app_facade.evt_dispatcher.dispatch(
                DownloadError(op_id, "Download error")
            )

        self.downloader.download_video.side_effect = dispatch_error
        output_dir = config["downloader.output_directory"]
        self.evt_expecter.expect(OperationError, "Download error").from_(
            Cmd.RetrieveVideo, video_id, output_dir
        )

    def test_fetch_video_subtitle(self):
        self.data_producer.video("source", None, path=Path("/tmp/source.mp4")).populate(
            self.data_facade
        )

        subtitle = "/tmp/source.srt"
        subtitle_language = config["subtitle.language"]
        self.ffmpeg_wrapper.probe.return_value = {
            "streams": [
                {
                    "index": 1,
                    "codec_type": "subtitle",
                    "codec_long_name": "subtitle",
                    "tags": {"language": subtitle_language},
                }
            ]
        }
        self.ffmpeg_wrapper.extract_stream.return_value = subtitle

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoSubtitleFetched, subtitle).from_(
            Cmd.FetchVideoSubtitle, video_id, subtitle_language
        )
