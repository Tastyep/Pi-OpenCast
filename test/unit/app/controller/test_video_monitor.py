from OpenCast.app.command import make_cmd
from OpenCast.app.command import video as Cmd
from OpenCast.app.controller.video_monitor import VideoMonitController
from OpenCast.domain.event import video as Evt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class VideoMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super().setUp()

        self.data_producer.video("source").video("source2").populate(self.data_facade)
        self.video_id = IdentityService.id_video("source")

        self.controller = VideoMonitController(
            self.app_facade, self.infra_facade, self.data_facade
        )

    async def test_list(self):
        req = self.make_request("GET", "/")
        resp = await self.route(self.controller.list, req)
        self.assertEqual(resp, (200, self.data_facade.video_repo.list()))

    async def test_get(self):
        req = self.make_request("GET", f"/{self.video_id}", {"id": str(self.video_id)})
        resp = await self.route(self.controller.get, req)
        self.assertEqual(resp, (200, self.data_facade.video_repo.get(self.video_id)))

    async def test_get_not_found(self):
        video_id = IdentityService.id_video("unknown")
        req = self.make_request("GET", f"/{video_id}", {"id": str(video_id)})
        resp = await self.route(self.controller.get, req)
        self.assertEqual(resp, (404, None))

    async def test_delete(self):
        req = self.make_request(
            "DELETE", f"/{self.video_id}", {"id": str(self.video_id)}
        )
        self.check_and_raise(make_cmd(Cmd.DeleteVideo, self.video_id), Evt.VideoDeleted)

        resp = await self.route(self.controller.delete, req)
        self.assertEqual(resp, (204, None))

    async def test_delete_not_found(self):
        video_id = IdentityService.id_video("unknown")
        req = self.make_request("DELETE", f"/{video_id}", {"id": str(video_id)})

        resp = await self.route(self.controller.delete, req)
        self.assertEqual(resp, (404, None))
