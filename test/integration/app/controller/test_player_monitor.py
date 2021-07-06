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
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase, asyncio


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
        playlist_id = IdentityService.id_playlist()
        video_id = IdentityService.id_video("source")
        self.data_producer.playlist(playlist_id, "test", []).video("source").populate(
            self.data_facade
        )
        self.expect_and_raise(
            make_cmd(PlayerCmd.PlayVideo, self.player_id, video_id, playlist_id),
            [
                {
                    "type": PlayerEvt.PlayerQueueUpdated,
                    "args": {"queue": playlist_id},
                },
                {
                    "type": PlayerEvt.PlayerStarted,
                    "args": {"state": PlayerState.PLAYING, "video_id": video_id},
                },
            ],
        )

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id), "playlist_id": str(playlist_id)},
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_play_video_not_found(self):
        playlist_id = IdentityService.id_playlist()
        video_id = IdentityService.id_video("source")
        self.data_producer.playlist(playlist_id, "test", []).populate(self.data_facade)

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id), "playlist_id": str(playlist_id)},
        )
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_play_playlist_not_found(self):
        playlist_id = IdentityService.id_playlist()
        video_id = IdentityService.id_video("source")
        self.data_producer.video("source").populate(self.data_facade)
        playlist_id = IdentityService.id_playlist()

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id), "playlist_id": str(playlist_id)},
        )
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_play_error(self):
        playlist_id = IdentityService.id_playlist()
        self.data_producer.playlist(playlist_id, "test").video("source").populate(
            self.data_facade
        )
        video_id = IdentityService.id_video("source")
        self.expect_and_error(
            make_cmd(PlayerCmd.PlayVideo, self.player_id, video_id, playlist_id),
            error="Error message",
        )

        resp = await self.client.post(
            "/api/player/play",
            params={"id": str(video_id), "playlist_id": str(playlist_id)},
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
        self.expect_and_raise(
            make_cmd(PlayerCmd.StopPlayer, self.player_id),
            [
                {
                    "type": PlayerEvt.PlayerStopped,
                    "args": {
                        "state": PlayerState.STOPPED,
                        "video_id": None,
                    },
                }
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
        self.expect_and_raise(
            make_cmd(PlayerCmd.TogglePlayerState, self.player_id),
            [
                {
                    "type": PlayerEvt.PlayerStateToggled,
                    "args": {"state": PlayerState.PAUSED},
                }
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
    async def test_seek_forward_short(self):
        self.expect_and_raise(
            make_cmd(PlayerCmd.SeekVideo, self.player_id, Player.SHORT_TIME_STEP),
            [{"type": PlayerEvt.VideoSeeked, "args": {}}],
        )

        resp = await self.client.post(
            "/api/player/seek", params={"forward": "true", "long": "false"}
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_seek_forward_long(self):
        self.expect_and_raise(
            make_cmd(PlayerCmd.SeekVideo, self.player_id, Player.LONG_TIME_STEP),
            [{"type": PlayerEvt.VideoSeeked, "args": {}}],
        )

        resp = await self.client.post(
            "/api/player/seek", params={"forward": "true", "long": "true"}
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_seek_backward_short(self):
        self.expect_and_raise(
            make_cmd(PlayerCmd.SeekVideo, self.player_id, -Player.SHORT_TIME_STEP),
            [{"type": PlayerEvt.VideoSeeked, "args": {}}],
        )

        resp = await self.client.post(
            "/api/player/seek", params={"forward": "false", "long": "false"}
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_seek_backward_long(self):
        self.expect_and_raise(
            make_cmd(PlayerCmd.SeekVideo, self.player_id, -Player.LONG_TIME_STEP),
            [{"type": PlayerEvt.VideoSeeked, "args": {}}],
        )

        resp = await self.client.post(
            "/api/player/seek", params={"forward": "false", "long": "true"}
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_seek_error(self):
        self.expect_and_error(
            make_cmd(PlayerCmd.SeekVideo, self.player_id, -Player.SHORT_TIME_STEP),
            error="Error message",
        )

        resp = await self.client.post(
            "/api/player/seek", params={"forward": "false", "long": "false"}
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
    async def test_subtitle_seek_forward(self):
        self.expect_and_raise(
            make_cmd(
                PlayerCmd.AdjustSubtitleDelay,
                self.player_id,
                Player.SUBTITLE_DELAY_STEP,
            ),
            [
                {
                    "type": PlayerEvt.SubtitleDelayUpdated,
                    "args": {
                        "delay": Player.SUBTITLE_DELAY_STEP,
                    },
                }
            ],
        )

        resp = await self.client.post(
            "/api/player/subtitle/seek", params={"forward": "true"}
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_subtitle_seek_backward(self):
        self.expect_and_raise(
            make_cmd(
                PlayerCmd.AdjustSubtitleDelay,
                self.player_id,
                -Player.SUBTITLE_DELAY_STEP,
            ),
            [
                {
                    "type": PlayerEvt.SubtitleDelayUpdated,
                    "args": {
                        "delay": -Player.SUBTITLE_DELAY_STEP,
                    },
                }
            ],
        )

        resp = await self.client.post(
            "/api/player/subtitle/seek", params={"forward": "false"}
        )
        body = await resp.json()
        player = self.data_facade.player_repo.get_player()
        self.assertEqual(200, resp.status)
        self.assertEqual(player.to_dict(), body)

    @unittest_run_loop
    async def test_subtitle_seek_error(self):
        self.expect_and_error(
            make_cmd(
                PlayerCmd.AdjustSubtitleDelay,
                self.player_id,
                Player.SUBTITLE_DELAY_STEP,
            ),
            error="Error message",
        )

        resp = await self.client.post(
            "/api/player/subtitle/seek", params={"forward": "true"}
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
    async def test_event_listening(self):
        async with self.client.ws_connect("/api/player/events") as ws:
            stop_evt = PlayerEvt.PlayerStopped(
                self.cmd_id,
                self.player_id,
                PlayerState.STOPPED,
                video_id=None,
            )
            self.evt_dispatcher.dispatch(stop_evt)
            await self.expect_ws_events(ws, [stop_evt])

            video_id = IdentityService.id_video("source")
            start_evt = PlayerEvt.PlayerStarted(
                self.cmd_id, self.player_id, PlayerState.PLAYING, video_id
            )
            self.evt_dispatcher.dispatch(start_evt)
            self.evt_dispatcher.dispatch(stop_evt)
            await self.expect_ws_events(ws, [start_evt, stop_evt])

    @unittest_run_loop
    async def test_invalid_event_listening(self):
        async with self.client.ws_connect("/api/player/events") as ws:
            video_id = IdentityService.id_video("source")
            video_evt = VideoEvt.VideoCreated(
                self.cmd_id,
                video_id,
                "source",
                IdentityService.random(),
                "album",
                "title",
                "http",
                "thumbnail",
            )
            self.evt_dispatcher.dispatch(video_evt)
            with self.assertRaises(asyncio.TimeoutError):
                await self.expect_ws_events(ws, [video_evt])
