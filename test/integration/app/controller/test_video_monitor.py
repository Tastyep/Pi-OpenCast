from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase, asyncio


class VideoMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(VideoMonitorControllerTest, self).setUp()
        self.player_id = IdentityService.id_player()
        self.video_id = IdentityService.id_video("source")

    @unittest_run_loop
    async def test_event_listening(self):
        async with self.client.ws_connect("/api/videos/events") as ws:
            cmd_id = IdentityService.id_command(VideoCmd.CreateVideo, self.video_id)
            created_evt = VideoEvt.VideoCreated(
                cmd_id, self.video_id, "source", "title", "album", "thumbnail"
            )
            self.evt_dispatcher.dispatch(created_evt)
            await self.expect_ws_events(ws, [created_evt])

            cmd_id = IdentityService.id_command(VideoCmd.RetrieveVideo, self.video_id)
            dl_evt = VideoEvt.VideoRetrieved(cmd_id, self.video_id, "path")
            self.evt_dispatcher.dispatch(created_evt)
            self.evt_dispatcher.dispatch(dl_evt)
            await self.expect_ws_events(ws, [created_evt, dl_evt])

    @unittest_run_loop
    async def test_invalid_event_listening(self):
        async with self.client.ws_connect("/api/videos/events") as ws:
            cmd_id = IdentityService.id_command(PlayerCmd.PlayVideo, self.player_id)
            player_evt = PlayerEvt.PlayerStarted(cmd_id, self.player_id, self.video_id)
            self.evt_dispatcher.dispatch(player_evt)
            with self.assertRaises(asyncio.TimeoutError):
                await self.expect_ws_events(ws, [player_evt])
