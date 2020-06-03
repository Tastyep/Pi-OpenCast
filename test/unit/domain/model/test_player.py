import OpenCast.domain.event.player as Evt
from OpenCast.config import config
from OpenCast.domain.error import DomainError
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.player_state import PlayerState
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService

from .util import ModelTestCase


class PlayerTest(ModelTestCase):
    def setUp(self):
        self.player = Player(None)

    def make_videos(self, video_count):
        return [self.make_video(f"source_{i}") for i in range(video_count)]

    def make_video(self, source="source_1"):
        return Video(IdentityService.id_video(source), source, None)

    def test_construction(self):
        self.assertEqual(70, self.player.volume)
        self.assertFalse(self.player.subtitle_state)
        self.assertEqual(0, self.player.subtitle_delay)
        self.assertEqual(PlayerState.STOPPED, self.player.state)

    def test_queue(self):
        video = self.make_video()
        self.player.queue(video)
        self.assertListEqual([video], self.player.video_queue)
        self.expect_events(self.player, Evt.VideoQueued)

    def test_queue_multiple_unrelated(self):
        videos = self.make_videos(video_count=3)
        for video in videos:
            self.player.queue(video)
        self.assertListEqual(videos, self.player.video_queue)

    def test_queue_multiple_related(self):
        videos = [
            Video(None, "source_1", "playlist_1"),
            Video(None, "source_2", None),
            Video(None, "source_3", "playlist_1"),
        ]
        for video in videos:
            self.player.queue(video)

        expected_queue = [videos[0], videos[2], videos[1]]
        self.assertListEqual(expected_queue, self.player.video_queue)

    def test_next(self):
        videos = self.make_videos(video_count=2)
        for video in videos:
            self.player.queue(video)
        config.load_from_dict({"player": {"loop_last": False}})
        self.assertEqual(videos[1], self.player.next_video())
        self.assertEqual(videos[1], self.player.next_video())

        self.player.play(self.player.next_video())
        self.assertEqual(None, self.player.next_video())

    def test_next_no_video(self):
        config.load_from_dict({"player": {"loop_last": True}})
        self.assertEqual(None, self.player.next_video())

    def test_prev(self):
        videos = self.make_videos(video_count=2)
        for video in videos:
            self.player.queue(video)
        self.assertEqual(videos[0], self.player.prev_video())
        self.player.play(self.player.next_video())
        self.assertEqual(videos[0], self.player.prev_video())

    def test_prev_no_video(self):
        self.assertEqual(None, self.player.prev_video())

    def test_play(self):
        video = self.make_video()
        self.player.queue(video)
        self.player.play(video)
        self.assertEqual(PlayerState.PLAYING, self.player.state)
        self.expect_events(self.player, Evt.VideoQueued, Evt.PlayerStarted)

    def test_play_unknown(self):
        video = self.make_video()
        with self.assertRaises(DomainError) as ctx:
            self.player.play(video)
        self.assertEqual(f"unknown video: {video}", str(ctx.exception))

    def test_stop(self):
        video = self.make_video()
        self.player.queue(video)
        self.player.play(video)
        self.player.stop()
        self.assertEqual(PlayerState.STOPPED, self.player.state)
        self.expect_events(
            self.player, Evt.VideoQueued, Evt.PlayerStarted, Evt.PlayerStopped
        )

    def test_stop_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.stop()
        self.assertEqual("the player is already stopped", str(ctx.exception))

    def test_pause(self):
        video = self.make_video()
        self.player.queue(video)
        self.player.play(video)
        self.player.pause()
        self.assertEqual(PlayerState.PAUSED, self.player.state)
        self.expect_events(
            self.player, Evt.VideoQueued, Evt.PlayerStarted, Evt.PlayerPaused
        )

    def test_pause_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.pause()
        self.assertEqual("the player is not started", str(ctx.exception))

    def test_unpause(self):
        video = self.make_video()
        self.player.queue(video)
        self.player.play(video)
        self.player.pause()
        self.player.unpause()
        self.assertEqual(PlayerState.PLAYING, self.player.state)
        self.expect_events(
            self.player,
            Evt.VideoQueued,
            Evt.PlayerStarted,
            Evt.PlayerPaused,
            Evt.PlayerUnpaused,
        )

    def test_unpause_not_paused(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.unpause()
        self.assertEqual("the player is not paused", str(ctx.exception))

    def test_volume(self):
        self.player.volume = -10
        self.assertEqual(0, self.player.volume)

        self.player.volume = 300
        self.assertEqual(200, self.player.volume)

        self.player.volume = 50
        self.assertEqual(50, self.player.volume)
        self.expect_events(self.player, Evt.VolumeUpdated)
