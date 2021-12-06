from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import album as AlbumCmd
from OpenCast.app.command import make_cmd
from OpenCast.domain.event import album as AlbumEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class AlbumMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(AlbumMonitorControllerTest, self).setUp()
        self.album_id = IdentityService.id_album("name")
        self.data_producer.album(self.album_id, "name").video("source1").video(
            "source2"
        ).album(IdentityService.id_album("name2"), "name2").populate(self.data_facade)

        self.album_repo = self.data_facade.album_repo
        self.albums = self.album_repo.list()

    @unittest_run_loop
    async def test_list(self):
        resp = await self.client.get("/api/albums/")
        body = await resp.json()
        albums = self.data_facade.album_repo.list()
        self.assertEqual(200, resp.status)
        self.assertEqual({"albums": [album.to_dict() for album in albums]}, body)

    @unittest_run_loop
    async def test_get(self):
        album = self.album_repo.get(self.album_id)
        resp = await self.client.get(f"/api/albums/{album.id}")
        body = await resp.json()
        self.assertEqual(200, resp.status)
        self.assertEqual(album.to_dict(), body)

    @unittest_run_loop
    async def test_get_not_found(self):
        album_id = IdentityService.random()
        resp = await self.client.get(f"/api/albums/{album_id}")
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_delete(self):
        album = self.album_repo.get(self.album_id)
        self.queueing_service.queue.return_value = []  # Ignore the queueing action
        self.expect_and_raise(
            make_cmd(AlbumCmd.DeleteAlbum, album.id),
            [
                {
                    "type": AlbumEvt.AlbumDeleted,
                    "args": {"ids": album.ids},
                }
            ],
        )

        resp = await self.client.delete(f"/api/albums/{album.id}")
        self.assertEqual(204, resp.status)

    @unittest_run_loop
    async def test_delete_not_found(self):
        album_id = IdentityService.random()
        resp = await self.client.delete(f"/api/albums/{album_id}")
        self.assertEqual(404, resp.status)
