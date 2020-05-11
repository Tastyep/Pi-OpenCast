import OpenCast.domain.event.player as Evt
from OpenCast.config import config
from OpenCast.domain.error import DomainError
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.player_state import PlayerState
from OpenCast.domain.model.video import Video

from .util import ModelTestCase


class PlayerTest(ModelTestCase):
    def test_construction(self):
        player = Player(None)
        self.assertEqual(100, player.volume)
        self.assertFalse(player.subtitle_state)
        self.assertEqual(0, player.subtitle_delay)
        self.assertEqual(PlayerState.STOPPED, player.state)

    def test_queue(self):
        player = Player(None)
        video = Video(None, "source", None)
        player.queue(video)
        self.assertListEqual([video], player.video_queue)
        self.expect_events(player, Evt.VideoQueued)

    def test_queue_multiple_unrelated(self):
        player = Player(None)
        videos = [
            Video(None, "source_1", None),
            Video(None, "source_2", None),
            Video(None, "source_3", None),
        ]
        for video in videos:
            player.queue(video)
        self.assertListEqual(videos, player.video_queue)

    def test_queue_multiple_related(self):
        player = Player(None)
        videos = [
            Video(None, "source_1", "playlist_1"),
            Video(None, "source_2", None),
            Video(None, "source_3", "playlist_1"),
        ]
        for video in videos:
            player.queue(video)

        expected_queue = [videos[0], videos[2], videos[1]]
        self.assertListEqual(expected_queue, player.video_queue)

    def test_next(self):
        player = Player(None)
        videos = [
            Video(None, "source_1", "1"),
            Video(None, "source_3", "2"),
        ]
        for video in videos:
            player.queue(video)
        config.load_from_dict({"player": {"loop_last": False}})
        self.assertEqual(videos[1], player.next_video())
        self.assertEqual(videos[1], player.next_video())

        player.play(player.next_video())
        self.assertEqual(None, player.next_video())

    def test_prev(self):
        player = Player(None)
        videos = [
            Video(None, "source_1", None),
            Video(None, "source_3", None),
        ]
        for video in videos:
            player.queue(video)
        self.assertEqual(videos[0], player.prev_video())
        player.play(player.next_video())
        self.assertEqual(videos[0], player.prev_video())

    def test_play(self):
        player = Player(None)
        video = Video(None, "source", None)
        player.queue(video)
        player.play(video)
        self.assertEqual(PlayerState.PLAYING, player.state)
        self.expect_events(player, Evt.VideoQueued, Evt.PlayerStarted)

    def test_play_unknown(self):
        player = Player(None)
        video = Video(None, "source", None)
        with self.assertRaises(DomainError) as ctx:
            player.play(video)
        self.assertEqual(f"unknown video: {video}", str(ctx.exception))

    def test_stop(self):
        player = Player(None)
        video = Video(None, "source", None)
        player.queue(video)
        player.play(video)
        player.stop()
        self.assertEqual(PlayerState.STOPPED, player.state)
        self.expect_events(
            player, Evt.VideoQueued, Evt.PlayerStarted, Evt.PlayerStopped
        )

    def test_stop_not_started(self):
        player = Player(None)
        with self.assertRaises(DomainError) as ctx:
            player.stop()
        self.assertEqual("the player is already stopped", str(ctx.exception))

    def test_pause(self):
        player = Player(None)
        video = Video(None, "source", None)
        player.queue(video)
        player.play(video)
        player.pause()
        self.assertEqual(PlayerState.PAUSED, player.state)
        self.expect_events(player, Evt.VideoQueued, Evt.PlayerStarted, Evt.PlayerPaused)

    def test_pause_not_started(self):
        player = Player(None)
        with self.assertRaises(DomainError) as ctx:
            player.pause()
        self.assertEqual("the player is not started", str(ctx.exception))

    def test_unpause(self):
        player = Player(None)
        video = Video(None, "source", None)
        player.queue(video)
        player.play(video)
        player.pause()
        player.unpause()
        self.assertEqual(PlayerState.PLAYING, player.state)
        self.expect_events(
            player,
            Evt.VideoQueued,
            Evt.PlayerStarted,
            Evt.PlayerPaused,
            Evt.PlayerUnpaused,
        )

    def test_unpause_not_paused(self):
        player = Player(None)
        with self.assertRaises(DomainError) as ctx:
            player.unpause()
        self.assertEqual("the player is not paused", str(ctx.exception))

    def test_volume(self):
        player = Player(None)

        player.volume = -10
        self.assertEqual(0, player.volume)

        player.volume = 300
        self.assertEqual(200, player.volume)

        player.volume = 50
        self.assertEqual(50, player.volume)
        self.expect_events(player, Evt.VolumeUpdated)
