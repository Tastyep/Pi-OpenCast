from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import make_cmd
from OpenCast.app.command import player as PlayerCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase, asyncio


class VideoMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(VideoMonitorControllerTest, self).setUp()
        self.data_producer.video("source").video("source2").populate(self.data_facade)
        self.player_id = IdentityService.id_player()
        self.video_id = IdentityService.id_video("source")

    @unittest_run_loop
    async def test_list(self):
        resp = await self.client.get("/api/videos/")
        body = await resp.json()
        videos = self.data_facade.video_repo.list()
        self.assertEqual(200, resp.status)
        self.assertEqual({"videos": [video.to_dict() for video in videos]}, body)

    @unittest_run_loop
    async def test_get(self):
        resp = await self.client.get(f"/api/videos/{self.video_id}")
        body = await resp.json()
        video = self.data_facade.video_repo.get(self.video_id)
        self.assertEqual(200, resp.status)
        self.assertEqual(video.to_dict(), body)

    @unittest_run_loop
    async def test_get_not_found(self):
        video_id = IdentityService.id_video("unknown")
        resp = await self.client.get(f"/api/videos/{video_id}")
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_delete(self):
        self.expect_and_raise(
            make_cmd(VideoCmd.DeleteVideo, self.video_id), VideoEvt.VideoDeleted
        )
        resp = await self.client.delete(f"/api/videos/{self.video_id}")
        self.assertEqual(204, resp.status)

    @unittest_run_loop
    async def test_delete_not_found(self):
        video_id = IdentityService.id_video("unknown")
        resp = await self.client.delete(f"/api/videos/{video_id}")
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_event_listening(self):
        async with self.client.ws_connect("/api/videos/events") as ws:
            cmd_id = IdentityService.id_command(VideoCmd.CreateVideo, self.video_id)
            created_evt = VideoEvt.VideoCreated(
                cmd_id, self.video_id, "source", "http", "title", "album", "thumbnail"
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
