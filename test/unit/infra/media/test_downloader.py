from test.util import TestCase
from unittest.mock import Mock, patch

from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.media.downloader import (
    Downloader,
    DownloadError,
    DownloadSuccess,
    Logger,
    Options,
)


class LoggerTest(TestCase):
    def setUp(self):
        self.impl = Mock()
        self.logger = Logger(self.impl)

    def test_downloading_log_missing_status(self):
        data = {}
        self.logger.log_download_progress(data)

        self.impl.debug.assert_not_called()
        self.impl.error.assert_not_called()

    def test_downloading_log(self):
        data = {
            "status": "downloading",
            "filename": "/tmp/media.mp4",
            "downloaded_bytes": 50,
            "total_bytes": 100,
            "speed": 10,
        }
        self.logger.log_download_progress(data)

        self.impl.debug.assert_called_with(
            "Downloading", filename="/tmp/media.mp4", ratio="50.00%", speed="10 bytes/s"
        )

    def test_downloading_log_missing_data(self):
        data = {
            "status": "downloading",
        }
        self.logger.log_download_progress(data)

        self.impl.debug.assert_called_with(
            "Downloading", filename="unknown", ratio="N/A", speed="0 bytes/s"
        )

    def test_error_log(self):
        data = {
            "status": "error",
            "filename": "/tmp/media.mp4",
        }
        self.logger.log_download_progress(data)

        self.impl.error.assert_called_with(
            "Downloading error", filename="/tmp/media.mp4", error=data
        )

    def test_error_log_missing_data(self):
        data = {
            "status": "error",
        }
        self.logger.log_download_progress(data)

        self.impl.error.assert_called_with(
            "Downloading error", filename="unknown", error=data
        )

    def test_finished_log(self):
        data = {
            "status": "finished",
            "filename": "/tmp/media.mp4",
            "total_bytes": 100,
        }
        self.logger.log_download_progress(data)

        self.impl.debug.assert_called_with(
            "Downloading success", filename="/tmp/media.mp4", size="100 bytes"
        )

    def test_finished_log_missing_data(self):
        data = {
            "status": "finished",
        }
        self.logger.log_download_progress(data)

        self.impl.debug.assert_called_with(
            "Downloading success", filename="unknown", size="0 bytes"
        )


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
        self.cache = Mock()
        self.cache.get.return_value = None
        self.dispatcher = Mock()
        self.downloader = Downloader(self.executor, self.cache, self.dispatcher)

    @patch("OpenCast.infra.media.downloader.Path")
    def test_download_video(self, path_cls):
        path_mock = path_cls.return_value
        path_mock.exists.return_value = True

        op_id = IdentityService.random()
        video_id = IdentityService.id_video("url")
        video_path = "/tmp/media.mp4"
        self.downloader.download_video(op_id, video_id, "url", video_path, Options())

        self.dispatcher.dispatch.assert_called_with(DownloadSuccess(op_id, video_path))

    def test_download_video_error(self):
        self.ydl.download.side_effect = RuntimeError("error")

        op_id = IdentityService.random()
        video_id = IdentityService.id_video("url")
        self.downloader.download_video(
            op_id, video_id, "url", "/tmp/media.mp4", Options()
        )

        self.dispatcher.dispatch.assert_called_with(DownloadError(op_id, "error"))

    @patch("OpenCast.infra.media.downloader.Path")
    def test_download_video_missing(self, path_cls):
        path_mock = path_cls.return_value
        path_mock.exists.return_value = False

        op_id = IdentityService.random()
        video_id = IdentityService.id_video("url")
        self.downloader.download_video(
            op_id, video_id, "url", "/tmp/media.mp4", Options()
        )

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

    def test_download_subtitle_not_found(self):
        self.ydl.download.side_effect = RuntimeError()
        self.assertEqual(
            None,
            self.downloader.download_subtitle(
                "url", dest="/tmp/media", lang="eng", exts=["vtt", "srt"]
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
