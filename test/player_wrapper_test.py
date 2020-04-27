from concurrent.futures import Future
from pathlib import Path

from mock import (
    Mock,
    PropertyMock,
    patch,
)
from OpenCast.player_wrapper import PlayerWrapper
from OpenCast.video import Video

from .util import TestCase


class PlayerWrapperTest(TestCase):
    def __init__(self, *args, **kwargs):
        self._player_mock = None
        super(TestCase, self).__init__(*args, **kwargs)

    def test_construction(self):
        with PlayerWrapper(lambda: None) as player:
            self.assertFalse(player.playing())

    def make_video(self, m_is_file, m_name, m_parent, url):
        path = Path(url)
        m_is_file.return_value = True
        m_parent.return_value = path.parent
        m_name.return_value = path.name
        return Video(url)

    def make_player_mock(self, exit_callback):
        self._player_mock = Mock()

        self._player_mock.exit_event = [exit_callback]
        return self._player_mock

    @patch("OpenCast.video.Path.parent", new_callable=PropertyMock)
    @patch("OpenCast.video.Path.name", new_callable=PropertyMock)
    @patch("OpenCast.video.Path.is_file")
    def test_play(self, m_is_file, m_name, m_parent):
        video = self.make_video(m_is_file, m_name, m_parent, "/tmp/test")
        f = Future()

        def fake_player_factory(path, command, dbus_name, exit_callback):
            self.assertEqual(path, "/tmp/test")
            player = self.make_player_mock(exit_callback)
            f.set_result(None)
            return player

        with PlayerWrapper(fake_player_factory) as player:
            player.play(video)
            f.result(timeout=5)
            self.assertNotEqual(None, self._player_mock)
            self.assertEqual(1, len(self._player_mock.exit_event))
            self._player_mock.exit_event[0](None, None)

    @patch("OpenCast.video.Path.parent", new_callable=PropertyMock)
    @patch("OpenCast.video.Path.name", new_callable=PropertyMock)
    @patch("OpenCast.video.Path.is_file")
    def test_play_queued(self, m_is_file, m_name, m_parent):
        video = self.make_video(m_is_file, m_name, m_parent, "/tmp/test")
        f = Future()

        def fake_player_factory(path, command, dbus_name, exit_callback):
            self.assertEqual(path, "/tmp/test")
            player = self.make_player_mock(exit_callback)
            f.set_result(None)
            return player

        with PlayerWrapper(fake_player_factory) as player:
            player.queue(video)
            player.play()
            f.result(timeout=5)
            self.assertNotEqual(None, self._player_mock)
            self.assertEqual(1, len(self._player_mock.exit_event))
            self._player_mock.exit_event[0](None, None)
