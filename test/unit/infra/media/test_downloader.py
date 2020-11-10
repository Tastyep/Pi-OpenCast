from test.util import TestCase
from unittest.mock import Mock, patch

from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.media.downloader import Downloader, DownloadError, DownloadSuccess


class DownloaderTest(TestCase):
    def setUp(self):
        patcher = patch("OpenCast.infra.media.downloader.YoutubeDL")
        self.addCleanup(patcher.stop)
        ydl_cls_mock = patcher.start()
        self.ydl = ydl_cls_mock.return_value

        def execute_handler(handler, *args):
            handler(*args)

        self.executor = Mock()
        self.executor.submit = Mock(side_effect=execute_handler)
        self.dispatcher = Mock()
        self.downloader = Downloader(self.executor, self.dispatcher)

    @patch("OpenCast.infra.media.downloader.Path")
    def test_download_video(self, path_cls):
        path_mock = path_cls.return_value
        path_mock.exists.return_value = True

        op_id = IdentityService.random()
        self.downloader.download_video(op_id, "url", "/tmp/media.mp4")

        self.dispatcher.dispatch.assert_called_with(DownloadSuccess(op_id))

    def test_download_video_error(self):
        self.ydl.download.side_effect = RuntimeError("error")

        op_id = IdentityService.random()
        self.downloader.download_video(op_id, "url", "/tmp/media.mp4")

        self.dispatcher.dispatch.assert_called_with(DownloadError(op_id, "error"))

    @patch("OpenCast.infra.media.downloader.Path")
    def test_download_video_missing(self, path_cls):
        path_mock = path_cls.return_value
        path_mock.exists.return_value = False

        op_id = IdentityService.random()
        self.downloader.download_video(op_id, "url", "/tmp/media.mp4")

        self.dispatcher.dispatch.assert_called_with(
            DownloadError(op_id, "video path points to non existent file")
        )

    def test_download_subtitle(self):
        subtitle = "/tmp/media.en.vtt"
        self.assertEqual(
            subtitle,
            self.downloader.download_subtitle(
                "url", dest="/tmp/media", lang="eng", exts=["vtt"]
            ),
        )

    def test_download_subtitle_second_choice(self):
        step = 0

        def raise_once(*args, **kwargs):
            nonlocal step

            step += 1
            if step == 1:
                raise RuntimeError()

        subtitle = "/tmp/media.en.srt"
        self.ydl.download.side_effect = raise_once
        self.assertEqual(
            subtitle,
            self.downloader.download_subtitle(
                "url", dest="/tmp/media", lang="eng", exts=["vtt", "srt"]
            ),
        )

    def test_download_metadata(self):
        metadata = {"url": "url", "title": "title"}
        self.ydl.extract_info.return_value = metadata
        self.assertEqual(
            metadata, self.downloader.download_metadata("url", process_ie_data=True)
        )

    def test_download_metadata_error(self):
        self.ydl.extract_info.side_effect = RuntimeError()
        self.assertEqual(
            None, self.downloader.download_metadata("url", process_ie_data=True)
        )
