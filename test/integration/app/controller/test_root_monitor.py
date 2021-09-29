from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import playlist as PlaylistCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.app.service.error import OperationError
from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase, asyncio


class RootMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(RootMonitorControllerTest, self).setUp()

    @unittest_run_loop
    async def test_event_listening(self):
        async with self.client.ws_connect("/api/events") as ws:
            playlist_id = IdentityService.id_playlist()
            cmd_id = IdentityService.id_command(PlaylistCmd.CreatePlaylist, playlist_id)
            created_evt = PlaylistEvt.PlaylistCreated(
                cmd_id,
                playlist_id,
                "name",
                [],
                False,
            )
            self.evt_dispatcher.dispatch(created_evt)
            await self.expect_ws_events(ws, [created_evt])

            update_cmd_id = IdentityService.id_command(
                PlaylistCmd.UpdatePlaylistContent, playlist_id
            )
            updated_evt = PlaylistEvt.PlaylistContentUpdated(
                update_cmd_id, playlist_id, []
            )
            self.evt_dispatcher.dispatch(created_evt)
            self.evt_dispatcher.dispatch(updated_evt)
            await self.expect_ws_events(ws, [created_evt, updated_evt])
