import functools
from test.util import TestCase
from unittest.mock import Mock

import OpenCast.infra.event.player as PlayerEvt
from OpenCast.infra.media.player_wrapper import EventType, PlayerError, PlayerWrapper


class PlayerWrapperTest(TestCase):
    def setUp(self):
        self.instance = Mock()
        self.player_impl = Mock()

        self.instance.media_player_new.return_value = self.player_impl

        def event_attach(evt, callback, *args, **kwargs):
            if evt is EventType.MediaPlayerEndReached:
                self.player_impl.stop.side_effect = functools.partial(
                    callback, evt, *args, **kwargs
                )

        evt_manager = Mock()
        self.player_impl.event_manager.return_value = evt_manager
        evt_manager.event_attach.side_effect = event_attach

        self.dispatcher = Mock()
        self.player = PlayerWrapper(self.instance, self.dispatcher)

    def test_play(self):
        self.player.play("/tmp/video.mp4")
        self.player_impl.set_media.assert_called_once()
        self.player_impl.play.assert_called_once()

    def test_stop(self):
        self.player.stop()
        self.player_impl.stop.assert_called_once()
        self.dispatcher.dispatch.assert_called_once_with(
            PlayerEvt.MediaEndReached(None)
        )

    def test_pause(self):
        self.player.pause()
        self.player_impl.pause.assert_called_once()

    def test_unpause(self):
        self.player.unpause()
        self.player_impl.pause.assert_called_once()

    def test_select_subtitle_stream(self):
        self.player.select_subtitle_stream(0)
        self.player_impl.is_playing.return_value = True
        self.player_impl.video_set_spu.assert_called_once_with(0)

    def test_select_subtitle_stream_while_stopped(self):
        self.player_impl.get_media.return_value = None
        with self.assertRaises(PlayerError) as ctx:
            self.player.select_subtitle_stream(0)

        self.assertEqual("the player is not started", str(ctx.exception))

    def test_toggle_subtitle(self):
        self.player.toggle_subtitle()
        self.player_impl.toggle_teletext.assert_called_once()

    def test_set_subtitle_delay(self):
        delay = 5
        self.player.set_subtitle_delay(delay)
        self.player_impl.video_set_spu_delay.assert_called_once_with(delay * 1000)

    def test_set_volume(self):
        volume = 5
        self.player.set_volume(volume)
        self.player_impl.audio_set_volume.assert_called_once_with(volume)

    def test_seek(self):
        duration = 5
        current_time = 1
        self.player_impl.get_time.return_value = current_time
        self.player.seek(duration)
        self.player_impl.set_time.assert_called_once_with(current_time + duration)
