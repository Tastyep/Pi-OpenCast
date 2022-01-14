from datetime import datetime, timedelta

from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import make_cmd
from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.workflow.player import (
    QueuePlaylistWorkflow,
    QueueVideoWorkflow,
    StreamPlaylistWorkflow,
    StreamVideoWorkflow,
)
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class PlayerMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(PlayerMonitorControllerTest, self).setUp()

        self.data_producer.player().populate(self.data_facade)
        self.player_id = IdentityService.id_player()
        self.cmd_id = IdentityService.id_command(PlayerCmd.PlayVideo, self.player_id)

    @unittest_run_loop
    async def test_get(self):
        resp = await self.client.get("/api/player/")
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_stream_simple(self):
        url = "http://video-provider/watch&video=id"
        self.source_service.is_playlist.return_value = False

        workflow = None

        def make_workflow(*args, **kwargs):
            nonlocal workflow
            workflow = StreamVideoWorkflow(*args, **kwargs)
            return workflow

        self.app_facade.workflow_factory.make_stream_video_workflow.side_effect = (
            make_workflow
        )

        resp = await self.client.post("/api/player/stream", params={"url": url})
        self.assertEqual(204, resp.status)
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    @unittest_run_loop
    async def test_stream_playlist(self):
        url = "http://video-provider/watch&video=id"
        self.source_service.is_playlist.return_value = True
        self.source_service.unfold.return_value = [url]
        workflow = None

        def make_workflow(*args, **kwargs):
            nonlocal workflow
            workflow = StreamPlaylistWorkflow(*args, **kwargs)
            return workflow

        self.app_facade.workflow_factory.make_stream_playlist_workflow.side_effect = (
            make_workflow
        )

        resp = await self.client.post("/api/player/stream", params={"url": url})
        self.assertEqual(204, resp.status)
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    @unittest_run_loop
    async def test_stream_playlist_non_unfoldable(self):
        url = "http://video-provider/watch&video=id"
        self.source_service.is_playlist.return_value = True
        self.source_service.unfold.return_value = []

        resp = await self.client.post("/api/player/stream", params={"url": url})
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Could not unfold the playlist URL",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_queue_simple(self):
        url = "http://video-provider/watch&video=id"
        self.source_service.is_playlist.return_value = False

        workflow = None

        def make_workflow(*args, **kwargs):
            nonlocal workflow
            workflow = QueueVideoWorkflow(*args, **kwargs)
            return workflow

        self.app_facade.workflow_factory.make_queue_video_workflow.side_effect = (
            make_workflow
        )

        resp = await self.client.post("/api/player/queue", params={"url": url})
        self.assertEqual(204, resp.status)
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    @unittest_run_loop
    async def test_queue_playlist(self):
        url = "http://video-provider/watch&video=id"
        self.source_service.is_playlist.return_value = True
        self.source_service.unfold.return_value = [url]
        workflow = None

        def make_workflow(*args, **kwargs):
            nonlocal workflow
            workflow = QueuePlaylistWorkflow(*args, **kwargs)
            return workflow

        self.app_facade.workflow_factory.make_queue_playlist_workflow.side_effect = (
            make_workflow
        )

        resp = await self.client.post("/api/player/queue", params={"url": url})
        self.assertEqual(204, resp.status)
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    @unittest_run_loop
    async def test_queue_playlist_non_unfoldable(self):
        url = "http://video-provider/watch&video=id"
        self.source_service.is_playlist.return_value = True
        self.source_service.unfold.return_value = []

        resp = await self.client.post("/api/player/queue", params={"url": url})
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Could not unfold the playlist URL",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_play(self):
        video_id = IdentityService.id_video("source")
        self.data_producer.select(Player, IdentityService.id_player()).video(
            "source", state=VideoState.READY
        ).populate(self.data_facade)
        self.expect_and_raise(
            make_cmd(PlayerCmd.PlayVideo, self.player_id, video_id),
            [
                {
                    "type": PlayerEvt.PlayerStateUpdated,
                    "args": {
                        "old_state": PlayerState.STOPPED,
                        "new_state": PlayerState.PLAYING,
                    },
                },
                {
                    "type": PlayerEvt.PlayerVideoUpdated,
                    "args": {
                        "old_video_id": None,
                        "new_video_id": video_id,
                    },
                },
                {
                    "type": VideoEvt.VideoStateUpdated,
                    "args": {
                        "old_state": VideoState.READY,
                        "new_state": VideoState.PLAYING,
                        "total_playing_duration": timedelta(),
                        "last_play": datetime.now(),
                    },
                },
            ],
        )

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id)},
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_play_video_not_found(self):
        video_id = IdentityService.id_video("source")

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id)},
        )
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_play_not_queued(self):
        video_id = IdentityService.id_video("source")
        self.data_producer.video("source").populate(self.data_facade)

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id)},
        )
        body = await resp.json()
        self.assertEqual(403, resp.status)
        self.assertEqual({"message": "the video is not queued", "details": {}}, body)

    @unittest_run_loop
    async def test_play_error(self):
        self.data_producer.select(Player, IdentityService.id_player()).video(
            "source"
        ).populate(self.data_facade)
        video_id = IdentityService.id_video("source")
        self.expect_and_error(
            make_cmd(PlayerCmd.PlayVideo, self.player_id, video_id),
            error="Error message",
        )

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id)},
        )
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_stop(self):
        self.data_producer.player().video("source").play("source").populate(
            self.data_facade
        )
        video_id = IdentityService.id_video("source")
        self.expect_and_raise(
            make_cmd(PlayerCmd.StopPlayer, self.player_id),
            [
                {
                    "type": PlayerEvt.PlayerStateUpdated,
                    "args": {
                        "old_state": PlayerState.PLAYING,
                        "new_state": PlayerState.STOPPED,
                    },
                },
                {
                    "type": PlayerEvt.PlayerVideoUpdated,
                    "args": {
                        "old_video_id": video_id,
                        "new_video_id": None,
                    },
                },
            ],
        )

        resp = await self.client.post("/api/player/stop")
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_stop_error(self):
        self.expect_and_error(
            make_cmd(PlayerCmd.StopPlayer, self.player_id), error="Error message"
        )

        resp = await self.client.post("/api/player/stop")
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_pause(self):
        self.data_producer.player().video("source").play("source").populate(
            self.data_facade
        )
        self.expect_and_raise(
            make_cmd(PlayerCmd.TogglePlayerState, self.player_id),
            [
                {
                    "type": PlayerEvt.PlayerStateUpdated,
                    "args": {
                        "old_state": PlayerState.PLAYING,
                        "new_state": PlayerState.PAUSED,
                    },
                },
            ],
        )

        resp = await self.client.post("/api/player/pause")
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_pause_error(self):
        self.expect_and_error(
            make_cmd(PlayerCmd.TogglePlayerState, self.player_id), error="Error message"
        )

        resp = await self.client.post("/api/player/pause")
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_seek(self):
        duration = 100
        self.expect_and_raise(
            make_cmd(PlayerCmd.SeekVideo, self.player_id, duration),
            [
                {
                    "type": PlayerEvt.VideoSeeked,
                    "args": {"duration": duration},
                }
            ],
        )

        resp = await self.client.post("/api/player/seek", params={"duration": duration})
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_seek_error(self):
        duration = 100
        self.expect_and_error(
            make_cmd(PlayerCmd.SeekVideo, self.player_id, duration),
            error="Error message",
        )

        resp = await self.client.post("/api/player/seek", params={"duration": duration})
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_volume(self):
        self.expect_and_raise(
            make_cmd(PlayerCmd.UpdateVolume, self.player_id, 80),
            [{"type": PlayerEvt.VolumeUpdated, "args": {"volume": 80}}],
        )

        resp = await self.client.post("/api/player/volume", params={"value": 80})
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_volume_error(self):
        self.expect_and_error(
            make_cmd(PlayerCmd.UpdateVolume, self.player_id, 80), error="Error message"
        )

        resp = await self.client.post("/api/player/volume", params={"value": 80})
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_subtitle_toggle(self):
        self.expect_and_raise(
            make_cmd(PlayerCmd.ToggleSubtitle, self.player_id),
            [{"type": PlayerEvt.SubtitleStateUpdated, "args": {"state": False}}],
        )

        resp = await self.client.post("/api/player/subtitle/toggle")
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_subtitle_toggle_error(self):
        self.expect_and_error(
            make_cmd(PlayerCmd.ToggleSubtitle, self.player_id), error="Error message"
        )
        resp = await self.client.post("/api/player/subtitle/toggle")
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_subtitle_seek(self):
        self.expect_and_raise(
            make_cmd(
                PlayerCmd.UpdateSubtitleDelay,
                self.player_id,
                100,
            ),
            [
                {
                    "type": PlayerEvt.SubtitleDelayUpdated,
                    "args": {
                        "delay": 100,
                    },
                }
            ],
        )

        resp = await self.client.post(
            "/api/player/subtitle/seek", params={"duration": 100}
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_subtitle_seek_error(self):
        self.expect_and_error(
            make_cmd(
                PlayerCmd.UpdateSubtitleDelay,
                self.player_id,
                100,
            ),
            error="Error message",
        )

        resp = await self.client.post(
            "/api/player/subtitle/seek", params={"duration": 100}
        )
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )
