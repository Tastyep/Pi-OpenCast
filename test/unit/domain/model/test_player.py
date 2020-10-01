import random
import string

import OpenCast.domain.event.player as Evt
from OpenCast.config import config
from OpenCast.domain.error import DomainError
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService

from .util import ModelTestCase


class PlayerTest(ModelTestCase):
    def setUp(self):
        self.player = Player(IdentityService.id_player())
        self.player.release_events()

    def make_videos(self, video_count, playlist_id=None):
        return [self.make_video(None, playlist_id) for i in range(video_count)]

    def make_video(self, source=None, playlist_id=None):
        if source is None:
            source = "".join(random.choice(string.ascii_letters) for _ in range(10))
        return Video(IdentityService.id_video(source), source, playlist_id)

    def test_construction(self):
        player = Player(IdentityService.id_player())
        self.assertEqual(70, player.volume)
        self.assertTrue(player.subtitle_state)
        self.assertEqual(0, player.subtitle_delay)
        self.assertEqual(PlayerState.STOPPED, player.state)
        self.expect_events(player, Evt.PlayerCreated)

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

    def test_queue_back(self):
        videos = self.make_videos(3)
        for video in videos:
            self.player.queue(video)

        expected = [video.id for video in videos]
        self.assertListEqual(expected, self.player.video_queue)

    def test_queue_front_empty_queue(self):
        videos = self.make_videos(3)
        for video in videos:
            self.player.queue(video, front=True)

        expected = [video.id for video in reversed(videos)]
        self.assertListEqual(expected, self.player.video_queue)

    def test_queue_front_playlist_empty_queue(self):
        playlist_id = IdentityService.id_playlist("playlist")
        videos = self.make_videos(3, playlist_id)
        for video in videos:
            self.player.queue(video, front=True)

        expected = [video.id for video in videos]
        self.assertListEqual(expected, self.player.video_queue)

    def test_queue_front_playlist_while_playing(self):
        playlist_id = IdentityService.id_playlist("playlist1")
        queued_videos = self.make_videos(3, playlist_id)
        for video in queued_videos:
            self.player.queue(video)

        self.player.play(queued_videos[1])

        playlist_id = IdentityService.id_playlist("playlist2")
        videos = self.make_videos(3, playlist_id)
        for video in videos:
            self.player.queue(video, front=True)

        expected = (
            [video.id for video in queued_videos[:2]]
            + [video.id for video in videos]
            + [video.id for video in queued_videos[2:]]
        )
        self.assertListEqual(expected, self.player.video_queue)

    def test_queue_front_merge_playlist(self):
        playlist_id = IdentityService.id_playlist("playlist")
        videos = self.make_videos(3, playlist_id)
        other_video = self.make_video("other")
        self.player.queue(videos[0], front=True)
        self.player.queue(videos[1], front=True)
        self.player.queue(other_video)
        self.player.queue(videos[2], front=True)

        expected_queue = [videos[0].id, videos[1].id, videos[2].id, other_video.id]
        self.assertListEqual(expected_queue, self.player.video_queue)

    def test_queue_no_merge_past_index(self):
        playlist_id = IdentityService.id_playlist("playlist")
        videos = self.make_videos(3, playlist_id)
        other_video = self.make_video("other")
        self.player.queue(videos[0], front=True)
        self.player.queue(videos[1], front=True)
        self.player.queue(other_video)
        self.player.play(other_video)
        self.player.queue(videos[2], front=True)

        expected_queue = [videos[0].id, videos[1].id, other_video.id, videos[2].id]
        self.assertListEqual(expected_queue, self.player.video_queue)

    def test_remove(self):
        video = self.make_video()
        self.player.queue(video)
        self.player.remove(video.id)

        self.expect_events(self.player, Evt.VideoQueued, Evt.VideoRemoved)

    def test_remove_not_found(self):
        video = self.make_video()
        with self.assertRaises(DomainError) as ctx:
            self.player.remove(video.id)
        self.assertEqual(f"unknown video: {video.id}", str(ctx.exception))

    def test_has_video(self):
        video = self.make_video()
        self.assertFalse(self.player.has_video(video.id))
        self.player.queue(video)
        self.assertTrue(self.player.has_video(video.id))

    def test_next(self):
        config.load_from_dict({"player": {"loop_last": False}})
        videos = self.make_videos(2)
        for video in videos:
            self.player.queue(video)
        self.assertEqual(videos[1].id, self.player.next_video())
        self.assertEqual(videos[1].id, self.player.next_video())

        video_id = self.player.next_video()
        next_video = next((video for video in videos if video.id == video_id))
        self.player.play(next_video)
        self.assertEqual(None, self.player.next_video())

    def test_next_no_video(self):
        config.load_from_dict({"player": {"loop_last": False}})
        self.assertEqual(None, self.player.next_video())

    def test_next_no_video_loop_last(self):
        config.load_from_dict({"player": {"loop_last": True}})
        self.assertEqual(None, self.player.next_video())

    def test_next_last_video(self):
        config.load_from_dict({"player": {"loop_last": False}})
        video = self.make_video()
        self.player.queue(video)
        self.assertEqual(None, self.player.next_video())

    def test_next_last_video_loop_last(self):
        config.load_from_dict({"player": {"loop_last": True}})
        video = self.make_video()
        self.player.queue(video)
        self.assertEqual(video.id, self.player.next_video())

    def test_toggle_pause(self):
        video = self.make_video()
        self.player.queue(video)
        self.player.play(video)
        self.player.toggle_pause()
        self.assertEqual(PlayerState.PAUSED, self.player.state)
        self.expect_events(
            self.player, Evt.VideoQueued, Evt.PlayerStarted, Evt.PlayerStateToggled
        )

    def test_toggle_pause_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.toggle_pause()
        self.assertEqual("the player is not started", str(ctx.exception))

    def test_toggle_pause_twice(self):
        video = self.make_video()
        self.player.queue(video)
        self.player.play(video)
        self.player.toggle_pause()
        self.player.toggle_pause()
        self.assertEqual(PlayerState.PLAYING, self.player.state)
        self.expect_events(
            self.player,
            Evt.VideoQueued,
            Evt.PlayerStarted,
            Evt.PlayerStateToggled,
            Evt.PlayerStateToggled,
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
        video = self.make_video()
        self.player.queue(video)
        self.player.play(video)
        self.player.seek_video()
        self.expect_events(
            self.player, Evt.VideoQueued, Evt.PlayerStarted, Evt.VideoSeeked
        )

    def test_seek_video_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.player.seek_video()
        self.assertEqual("the player is not started", str(ctx.exception))
