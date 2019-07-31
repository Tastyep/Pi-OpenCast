from mock import (
    ANY,
    Mock,
    patch,
)
from OpenCast.controller import Controller
from OpenCast.video import Video

from .util import TestCase


class ControllerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = Mock()
        cls.downloader = Mock()
        cls.controller = Controller(cls.player, cls.downloader)

    def tearDown(self):
        self.player.reset_mock()
        self.downloader.reset_mock()

    def test_stream_video_simple_url(self):
        self.controller.stream_video('url')
        self.downloader.queue.assert_called_once_with(
            [Video('url')], ANY, True)

    @patch('OpenCast.controller.Video')
    def test_stream_video_local_path(self, video_mock):
        video_mock.is_local.return_value = True

        self.controller.stream_video('url')
        self.player.play.assert_called_once_with(ANY)

    @patch('OpenCast.controller.uuid')
    def test_stream_video_playlist(self, uuid_mock):
        uuid_mock.uuid4.return_value = 'id'
        self.downloader.extract_playlist.return_value = ['url1', 'url2']

        self.controller.stream_video('/playlist')
        self.downloader.extract_playlist.assert_called_once_with('/playlist')
        self.downloader.queue.assert_called_once_with(
            [Video('url1', playlist_id='id'), Video('url2', playlist_id='id')],
            ANY, True)

    def test_queue_video_simple_url(self):
        self.controller.queue_video('url')
        self.downloader.queue.assert_called_once_with(
                [Video('url')], ANY, False)

    @patch('OpenCast.controller.Video')
    def test_queue_video_local_path(self, video_mock):
        video_mock.is_local.return_value = True

        self.controller.queue_video('url')
        self.player.queue.assert_called_once_with(ANY)

    @patch('OpenCast.controller.uuid')
    def test_queue_video_playlist(self, uuid_mock):
        uuid_mock.uuid4.return_value = 'id'
        self.downloader.extract_playlist.return_value = ['url1', 'url2']

        self.controller.queue_video('/playlist')
        self.downloader.extract_playlist.assert_called_once_with('/playlist')
        self.downloader.queue.assert_called_once_with(
            [Video('url1', playlist_id='id'), Video('url2', playlist_id='id')],
            ANY, False)

    def test_stop_video(self):
        self.controller.stop_video()
        self.player.stop.assert_called_once()

    def test_prev_video(self):
        self.controller.prev_video()
        self.player.prev.assert_called_once()

    def test_next_video(self):
        self.controller.next_video()
        self.player.next.assert_called_once()

    def test_play_pause_video(self):
        self.controller.play_pause_video()
        self.player.play_pause.assert_called_once_with()

    def test_change_volume(self):
        self.controller.change_volume(True)
        self.player.change_volume.assert_called_once_with(True)

    def test_seek_time(self):
        self.controller.seek_time(True, True)
        self.player.seek.assert_called_once_with(True, True)
