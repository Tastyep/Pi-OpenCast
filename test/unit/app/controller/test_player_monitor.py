from unittest.mock import Mock

from OpenCast.app.command import make_cmd
from OpenCast.app.command import player as Cmd
from OpenCast.app.controller.player_monitor import Player, PlayerMonitController
from OpenCast.app.workflow.player import (
    QueuePlaylistWorkflow,
    QueueVideoWorkflow,
    StreamPlaylistWorkflow,
    StreamVideoWorkflow,
)
from OpenCast.domain.event import player as Evt
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class PlayerMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super().setUp()

        self.data_producer.player().populate(self.data_facade)

        self.source_service = Mock()
        self.service_factory = Mock()
        self.service_factory.make_source_service.return_value = self.source_service

        self.controller = PlayerMonitController(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )
        self.player_id = IdentityService.id_player()

    async def test_get(self):
        req = self.make_request("GET", "/")
        resp = await self.route(self.controller.get, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_stream_simple(self):
        url = "http://video-provider/watch&video=id"
        req = self.make_request("POST", "/stream", query={"url": url})
        self.source_service.is_playlist.return_value = False
        workflow = None

        def make_workflow(*args, **kwargs):
            nonlocal workflow
            workflow = StreamVideoWorkflow(*args, **kwargs)
            return workflow

        self.app_facade.workflow_factory.make_stream_video_workflow.side_effect = (
            make_workflow
        )
        resp = await self.route(self.controller.stream, req)
        self.assertEqual(resp, (200, None))
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    async def test_stream_playlist(self):
        url = "http://video-provider/watch&video=id"
        req = self.make_request("POST", "/stream", query={"url": url})
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
        resp = await self.route(self.controller.stream, req)
        self.assertEqual(resp, (200, None))
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    async def test_queue_simple(self):
        url = "http://video-provider/watch&video=id"
        req = self.make_request("POST", "/queue", query={"url": url})
        self.source_service.is_playlist.return_value = False
        workflow = None

        def make_workflow(*args, **kwargs):
            nonlocal workflow
            workflow = QueueVideoWorkflow(*args, **kwargs)
            return workflow

        self.app_facade.workflow_factory.make_queue_video_workflow.side_effect = (
            make_workflow
        )
        resp = await self.route(self.controller.queue, req)
        self.assertEqual(resp, (200, None))
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    async def test_queue_playlist(self):
        url = "http://video-provider/watch&video=id"
        req = self.make_request("POST", "/queue", query={"url": url})
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
        resp = await self.route(self.controller.queue, req)
        self.assertEqual(resp, (200, None))
        self.app_facade.workflow_manager.start.assert_called_with(workflow)

    async def test_play(self):
        self.data_producer.video("source", None).populate(self.data_facade)
        video_id = IdentityService.id_video("source")
        req = self.make_request("POST", "/play", query={"id": str(video_id)})
        self.check_and_raise(
            make_cmd(Cmd.PlayVideo, self.player_id, video_id),
            Evt.PlayerStarted,
            video_id,
        )

        resp = await self.route(self.controller.play, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_play_not_found(self):
        video_id = IdentityService.id_video("source")
        req = self.make_request("POST", "/play", query={"id": str(video_id)})

        resp = await self.route(self.controller.play, req)
        self.assertEqual(resp, (404, None))

    async def test_play_error(self):
        self.data_producer.video("source", None).populate(self.data_facade)
        video_id = IdentityService.id_video("source")
        req = self.make_request("POST", "/play", query={"id": str(video_id)})
        self.check_and_error(make_cmd(Cmd.PlayVideo, self.player_id, video_id))

        resp = await self.route(self.controller.play, req)
        self.assertEqual(resp, (400, None))

    async def test_stop(self):
        req = self.make_request("POST", "/stop")
        self.check_and_raise(
            make_cmd(Cmd.StopPlayer, self.player_id), Evt.PlayerStopped
        )

        resp = await self.route(self.controller.stop, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_stop_error(self):
        req = self.make_request("POST", "/stop")
        self.check_and_error(make_cmd(Cmd.StopPlayer, self.player_id))

        resp = await self.route(self.controller.stop, req)
        self.assertEqual(resp, (400, None))

    async def test_pause(self):
        req = self.make_request("POST", "/pause")
        self.check_and_raise(
            make_cmd(Cmd.TogglePlayerState, self.player_id),
            Evt.PlayerStateToggled,
            PlayerState.PAUSED,
        )

        resp = await self.route(self.controller.pause, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_pause_error(self):
        req = self.make_request("POST", "/pause")
        self.check_and_error(make_cmd(Cmd.TogglePlayerState, self.player_id))

        resp = await self.route(self.controller.pause, req)
        self.assertEqual(resp, (400, None))

    async def test_seek_forward_short(self):
        req = self.make_request(
            "POST", "/seek", query={"forward": "true", "long": "false"}
        )
        self.check_and_raise(
            make_cmd(Cmd.SeekVideo, self.player_id, Player.SHORT_TIME_STEP),
            Evt.VideoSeeked,
        )

        resp = await self.route(self.controller.seek, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_seek_forward_long(self):
        req = self.make_request(
            "POST", "/seek", query={"forward": "true", "long": "true"}
        )
        self.check_and_raise(
            make_cmd(Cmd.SeekVideo, self.player_id, Player.LONG_TIME_STEP),
            Evt.VideoSeeked,
        )

        resp = await self.route(self.controller.seek, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_seek_backward_short(self):
        req = self.make_request(
            "POST", "/seek", query={"forward": "false", "long": "false"}
        )
        self.check_and_raise(
            make_cmd(Cmd.SeekVideo, self.player_id, -Player.SHORT_TIME_STEP),
            Evt.VideoSeeked,
        )

        resp = await self.route(self.controller.seek, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_seek_backward_long(self):
        req = self.make_request(
            "POST", "/seek", query={"forward": "false", "long": "true"}
        )
        self.check_and_raise(
            make_cmd(Cmd.SeekVideo, self.player_id, -Player.LONG_TIME_STEP),
            Evt.VideoSeeked,
        )

        resp = await self.route(self.controller.seek, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_seek_error(self):
        req = self.make_request(
            "POST", "/seek", query={"forward": "true", "long": "true"}
        )
        self.check_and_error(
            make_cmd(Cmd.SeekVideo, self.player_id, Player.LONG_TIME_STEP)
        )

        resp = await self.route(self.controller.seek, req)
        self.assertEqual(resp, (400, None))

    async def test_volume(self):
        req = self.make_request("POST", "/volume", query={"value": 80})
        self.check_and_raise(
            make_cmd(Cmd.UpdateVolume, self.player_id, 80),
            Evt.VolumeUpdated,
            80,
        )

        resp = await self.route(self.controller.volume, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_volume_error(self):
        req = self.make_request("POST", "/volume", query={"value": 80})
        self.check_and_error(make_cmd(Cmd.UpdateVolume, self.player_id, 80))

        resp = await self.route(self.controller.volume, req)
        self.assertEqual(resp, (400, None))

    async def test_subtitle_toggle(self):
        req = self.make_request("POST", "/subtitle/toggle")
        self.check_and_raise(
            make_cmd(Cmd.ToggleSubtitle, self.player_id),
            Evt.SubtitleStateUpdated,
            False,
        )

        resp = await self.route(self.controller.subtitle_toggle, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_subtitle_toggle_error(self):
        req = self.make_request("POST", "/subtitle_toggle")
        self.check_and_error(make_cmd(Cmd.ToggleSubtitle, self.player_id))

        resp = await self.route(self.controller.subtitle_toggle, req)
        self.assertEqual(resp, (400, None))

    async def test_subtitle_seek_forward(self):
        req = self.make_request("POST", "/subtitle/seek", query={"forward": "true"})
        self.check_and_raise(
            make_cmd(
                Cmd.AdjustSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP
            ),
            Evt.SubtitleDelayUpdated,
            Player.SUBTITLE_DELAY_STEP,
        )

        resp = await self.route(self.controller.subtitle_seek, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_subtitle_seek_backward(self):
        req = self.make_request("POST", "/subtitle/seek", query={"forward": "false"})
        self.check_and_raise(
            make_cmd(
                Cmd.AdjustSubtitleDelay, self.player_id, -Player.SUBTITLE_DELAY_STEP
            ),
            Evt.SubtitleDelayUpdated,
            -Player.SUBTITLE_DELAY_STEP,
        )

        resp = await self.route(self.controller.subtitle_seek, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_subtitle_seek_error(self):
        req = self.make_request("POST", "/subtitle_seek", query={"forward": "true"})
        self.check_and_error(
            make_cmd(
                Cmd.AdjustSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP
            )
        )

        resp = await self.route(self.controller.subtitle_seek, req)
        self.assertEqual(resp, (400, None))
