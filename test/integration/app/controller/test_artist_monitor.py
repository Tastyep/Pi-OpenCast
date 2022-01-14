from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import artist as ArtistCmd
from OpenCast.app.command import make_cmd
from OpenCast.domain.event import artist as ArtistEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class ArtistMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(ArtistMonitorControllerTest, self).setUp()
        self.artist_id = IdentityService.id_artist("name")
        self.data_producer.artist(self.artist_id, "name").video("source1").video(
            "source2"
        ).artist(IdentityService.id_artist("name2"), "name2").populate(self.data_facade)

        self.artist_repo = self.data_facade.artist_repo
        self.artists = self.artist_repo.list()

    @unittest_run_loop
    async def test_list(self):
        resp = await self.client.get("/api/artists/")
        body = await resp.json()
        artists = self.data_facade.artist_repo.list()
        self.assertEqual(200, resp.status)
        self.assertEqual({"artists": [artist.to_dict() for artist in artists]}, body)

    @unittest_run_loop
    async def test_get(self):
        artist = self.artist_repo.get(self.artist_id)
        resp = await self.client.get(f"/api/artists/{artist.id}")
        body = await resp.json()
        self.assertEqual(200, resp.status)
        self.assertEqual(artist.to_dict(), body)

    @unittest_run_loop
    async def test_get_not_found(self):
        artist_id = IdentityService.random()
        resp = await self.client.get(f"/api/artists/{artist_id}")
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_delete(self):
        artist = self.artist_repo.get(self.artist_id)
        self.queueing_service.queue.return_value = []  # Ignore the queueing action
        self.expect_and_raise(
            make_cmd(ArtistCmd.DeleteArtist, artist.id),
            [
                {
                    "type": ArtistEvt.ArtistDeleted,
                    "args": {"ids": artist.ids},
                }
            ],
        )

        resp = await self.client.delete(f"/api/artists/{artist.id}")
        self.assertEqual(204, resp.status)

    @unittest_run_loop
    async def test_delete_not_found(self):
        artist_id = IdentityService.random()
        resp = await self.client.delete(f"/api/artists/{artist_id}")
        self.assertEqual(404, resp.status)
