from aiohttp.test_utils import unittest_run_loop

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
        self.cmd_id = IdentityService.id_command(VideoCmd.CreateVideo, self.video_id)

    @unittest_run_loop
    async def test_event_listening(self):
        async with self.client.ws_connect(f"/api/videos/events") as ws:
            id_evt = VideoEvt.VideoIdentified(self.cmd_id, self.video_id, {})
            self.evt_dispatcher.dispatch(id_evt)
            await self.expect_ws_events(ws, [id_evt])

            del_evt = VideoEvt.VideoDeleted(self.cmd_id, self.video_id)
            self.evt_dispatcher.dispatch(del_evt)
            self.evt_dispatcher.dispatch(id_evt)
            await self.expect_ws_events(ws, [del_evt, id_evt])

    @unittest_run_loop
    async def test_invalid_event_listening(self):
        async with self.client.ws_connect(f"/api/videos/events") as ws:
            player_evt = PlayerEvt.PlayerStopped(self.cmd_id, self.player_id)
            self.evt_dispatcher.dispatch(player_evt)
            with self.assertRaises(asyncio.TimeoutError):
                await self.expect_ws_events(ws, [player_evt])
