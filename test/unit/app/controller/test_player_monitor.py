import asyncio
from unittest.mock import Mock

from OpenCast.app.command import make_cmd
from OpenCast.app.command import player as Cmd
from OpenCast.app.controller.player_monitor import PlayerMonitController
from OpenCast.domain.event import player as Evt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class PlayerMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super().setUp()

        self.data_producer.player().populate(self.data_facade)

        self.service_factory = Mock()
        self.controller = PlayerMonitController(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )
        self.player_id = IdentityService.id_player()

    async def test_get(self):
        req = self.make_request("GET", "/")
        resp = await self.route(self.controller._get, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_pick_video(self):
        video_id = IdentityService.id_video("source")
        req = self.make_request("POST", "/video", {"id": video_id})
        self.set_cmd_response(
            make_cmd(Cmd.PickVideo, self.player_id, video_id),
            Evt.PlayerStarted,
            video_id,
        )

        resp = await self.route(self.controller._pick_video, req)
        self.assertEqual(resp, (200, self.data_facade.player_repo.get_player()))

    async def test_pick_video_error(self):
        video_id = IdentityService.id_video("source")
        req = self.make_request("POST", "/video", {"id": video_id})
        self.set_cmd_error(make_cmd(Cmd.PickVideo, self.player_id, video_id))

        resp = await self.route(self.controller._pick_video, req)
        self.assertEqual(resp, (400, None))
