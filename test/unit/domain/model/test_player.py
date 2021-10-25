import OpenCast.domain.event.player as Evt
from OpenCast.domain.error import DomainError
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.service.identity import IdentityService

from .util import ModelTestCase


class PlayerTest(ModelTestCase):
    def setUp(self):
        self.queue_id = IdentityService.id_playlist()
        self.player = Player(IdentityService.id_player(), self.queue_id)
        self.player.release_events()

    def test_construction(self):
        player = Player(IdentityService.id_player(), self.queue_id)
        self.assertEqual(self.queue_id, player.queue)
        self.assertEqual(None, player.video_id)
        self.assertEqual(PlayerState.STOPPED, player.state)
        self.assertEqual(70, player.volume)
        self.assertTrue(player.subtitle_state)
        self.assertEqual(0, player.subtitle_delay)
        self.expect_events(player, Evt.PlayerCreated)

    def test_play(self):
        video_id = IdentityService.id_video("source")
        self.player.play(video_id)
        self.assertEqual(PlayerState.PLAYING, self.player.state)
        self.assertEqual(video_id, self.player.video_id)
        self.expect_events(self.player, Evt.PlayerStateUpdated)

    def test_play_already_playing(self):
        video_id = IdentityService.id_video("source")
        self.player.play(video_id)
        with self.assertRaises(DomainError) as ctx:
            self.player.play(video_id)
        self.assertEqual("the player is already started", str(ctx.exception))

    def test_stop(self):
        self.player.state = PlayerState.PLAYING
        self.player.release_events()

        self.player.stop()
        self.assertEqual(PlayerState.STOPPED, self.player.state)
        self.assertEqual(None, self.player.video_id)
        self.expect_events(self.player, Evt.PlayerStateUpdated)

    def test_stop_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.stop()
        self.assertEqual("the player is not started", str(ctx.exception))

    def test_toggle_pause(self):
        video_id = IdentityService.id_video("source")
        self.player.play(video_id)
        self.player.toggle_pause()
        self.assertEqual(PlayerState.PAUSED, self.player.state)
        self.expect_events(self.player, Evt.PlayerStateUpdated, Evt.PlayerStateUpdated)

    def test_toggle_pause_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.toggle_pause()
        self.assertEqual("the player is not started", str(ctx.exception))

    def test_toggle_pause_twice(self):
        video_id = IdentityService.id_video("source")
        self.player.play(video_id)
        self.player.toggle_pause()
        self.player.toggle_pause()
        self.assertEqual(PlayerState.PLAYING, self.player.state)
        self.expect_events(
            self.player,
            Evt.PlayerStateUpdated,
            Evt.PlayerStateUpdated,
            Evt.PlayerStateUpdated,
        )

    def test_volume(self):
        self.player.volume = -10
        self.assertEqual(0, self.player.volume)

        self.player.volume = 300
        self.assertEqual(200, self.player.volume)

        self.player.volume = 50
        self.assertEqual(50, self.player.volume)
        self.expect_events(
            self.player, Evt.VolumeUpdated, Evt.VolumeUpdated, Evt.VolumeUpdated
        )

    def test_seek_video(self):
        video_id = IdentityService.id_video("source")
        self.player.play(video_id)
        self.player.seek_video()
        self.expect_events(self.player, Evt.PlayerStateUpdated, Evt.VideoSeeked)

    def test_seek_video_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.seek_video()
        self.assertEqual("the player is not started", str(ctx.exception))
