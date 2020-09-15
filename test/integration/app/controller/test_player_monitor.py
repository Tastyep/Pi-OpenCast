from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import player as PlayerCmd
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase, asyncio


class PlayerMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(PlayerMonitorControllerTest, self).setUp()
        self.player_id = IdentityService.id_player()
        self.video_id = IdentityService.id_video("source")
        self.cmd_id = IdentityService.id_command(PlayerCmd.PlayVideo, self.player_id)

    @unittest_run_loop
    async def test_event_listening(self):
        async with self.client.ws_connect(f"/api/player/events") as ws:
            stop_evt = PlayerEvt.PlayerStopped(self.cmd_id, self.player_id)
            self.evt_dispatcher.dispatch(stop_evt)
            await self.expect_ws_events(ws, [stop_evt])

            start_evt = PlayerEvt.PlayerStarted(
                self.cmd_id, self.player_id, self.video_id
            )
            self.evt_dispatcher.dispatch(start_evt)
            self.evt_dispatcher.dispatch(stop_evt)
            await self.expect_ws_events(ws, [start_evt, stop_evt])

    @unittest_run_loop
    async def test_invalid_event_listening(self):
        async with self.client.ws_connect(f"/api/player/events") as ws:
            video_evt = VideoEvt.VideoDeleted(self.cmd_id, self.video_id)
            self.evt_dispatcher.dispatch(video_evt)
            with self.assertRaises(asyncio.TimeoutError):
                await self.expect_ws_events(ws, [video_evt])
