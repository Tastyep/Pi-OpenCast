from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import make_cmd
from OpenCast.app.command import playlist as PlaylistCmd
from OpenCast.app.service.error import OperationError
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class PlaylistMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(PlaylistMonitorControllerTest, self).setUp()
        self.data_producer.playlist("playlist1").video("source1").video(
            "source2"
        ).playlist("playlist2").populate(self.data_facade)

        self.playlist_repo = self.data_facade.playlist_repo
        self.video_repo = self.data_facade.video_repo
        self.playlists = self.playlist_repo.list()

    @unittest_run_loop
    async def test_create(self):
        playlist_id = None

        def make_and_respond(cmd):
            nonlocal playlist_id

            playlist_id = cmd.model_id
            self.data_producer.playlist(
                id=playlist_id, name=cmd.name, ids=cmd.ids
            ).populate(self.data_facade)
            self.app_facade.evt_dispatcher.dispatch(
                PlaylistEvt.PlaylistCreated(cmd.id, playlist_id, cmd.name, cmd.ids)
            )

        self.hook_cmd(PlaylistCmd.CreatePlaylist, make_and_respond)
        resp = await self.client.post("/api/playlists/", json={"name": "test_playlist"})
        body = await resp.json()
        playlist = self.playlist_repo.get(playlist_id)
        self.assertEqual(200, resp.status)
        self.assertEqual(playlist.to_dict(), body)

    @unittest_run_loop
    async def test_create_validation_error(self):
        resp = await self.client.post("/api/playlists/", json={"name": 5})
        body = await resp.json()
        self.assertEqual(422, resp.status)
        self.assertEqual(
            {"name": ["Not a valid string."]},
            body,
        )

    @unittest_run_loop
    async def test_create_service_error(self):
        self.error_on(PlaylistCmd.CreatePlaylist, "Error message.")
        resp = await self.client.post("/api/playlists/", json={"name": "test_playlist"})
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "error": {
                    "detail": None,
                    "message": "Error message.",
                }
            },
            body,
        )

    @unittest_run_loop
    async def test_list(self):
        resp = await self.client.get("/api/playlists/")
        body = await resp.json()
        playlists = self.data_facade.playlist_repo.list()
        self.assertEqual(200, resp.status)
        self.assertEqual(
            {"playlists": [playlist.to_dict() for playlist in playlists]}, body
        )

    @unittest_run_loop
    async def test_get(self):
        playlist = self.playlists[0]
        resp = await self.client.get(f"/api/playlists/{playlist.id}")
        body = await resp.json()
        self.assertEqual(200, resp.status)
        self.assertEqual(playlist.to_dict(), body)

    @unittest_run_loop
    async def test_get_not_found(self):
        playlist_id = IdentityService.id_playlist()
        resp = await self.client.get(f"/api/playlists/{playlist_id}")
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_list_videos(self):
        playlist = self.playlists[0]
        resp = await self.client.get(f"/api/playlists/{playlist.id}/videos")
        body = await resp.json()
        videos = self.video_repo.list(playlist.ids)
        self.assertEqual(200, resp.status)
        self.assertEqual({"videos": [video.to_dict() for video in videos]}, body)

    @unittest_run_loop
    async def test_list_videos_not_found(self):
        playlist_id = IdentityService.id_playlist()
        resp = await self.client.get(f"/api/playlists/{playlist_id}/videos")
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_update(self):
        req_body = {"name": "test_playlist", "ids": [str(IdentityService.random())]}
        playlist = self.playlists[0]
        self.expect_and_raise_l(
            [
                {
                    "cmd": make_cmd(
                        PlaylistCmd.RenamePlaylist, playlist.id, req_body["name"]
                    ),
                    "evt": PlaylistEvt.PlaylistRenamed,
                    "args": {"name": req_body["name"]},
                },
                {
                    "cmd": make_cmd(
                        PlaylistCmd.UpdatePlaylistContent, playlist.id, req_body["ids"]
                    ),
                    "evt": PlaylistEvt.PlaylistContentUpdated,
                    "args": {"ids": req_body["ids"]},
                },
            ]
        )

        resp = await self.client.patch(f"/api/playlists/{playlist.id}", json=req_body)
        body = await resp.json()
        self.assertEqual(200, resp.status)
        self.assertEqual(playlist.to_dict(), body)

    @unittest_run_loop
    async def test_update_not_found(self):
        playlist_id = IdentityService.id_playlist()
        req_body = {"name": "test_playlist", "ids": [str(IdentityService.random())]}
        resp = await self.client.patch(f"/api/playlists/{playlist_id}", json=req_body)
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_update_validation_error(self):
        req_body = {"name": 2, "ids": [str(IdentityService.random())]}
        playlist = self.playlists[0]

        resp = await self.client.patch(f"/api/playlists/{playlist.id}", json=req_body)
        body = await resp.json()
        self.assertEqual(422, resp.status)
        self.assertEqual(
            {"name": ["Not a valid string."]},
            body,
        )

    @unittest_run_loop
    async def test_update_error(self):
        req_body = {"name": "test_playlist", "ids": [str(IdentityService.random())]}
        playlist = self.playlists[0]
        self.expect_and_raise_l(
            [
                {
                    "cmd": make_cmd(
                        PlaylistCmd.RenamePlaylist, playlist.id, req_body["name"]
                    ),
                    "evt": PlaylistEvt.PlaylistRenamed,
                    "args": {"name": req_body["name"]},
                },
                {
                    "cmd": make_cmd(
                        PlaylistCmd.UpdatePlaylistContent, playlist.id, req_body["ids"]
                    ),
                    "evt": OperationError,
                    "args": {"error": "Error message."},
                },
            ]
        )

        resp = await self.client.patch(f"/api/playlists/{playlist.id}", json=req_body)
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "error": {
                    "detail": None,
                    "message": "Error message.",
                }
            },
            body,
        )

    @unittest_run_loop
    async def test_delete(self):
        playlist = self.playlists[0]
        self.expect_and_raise(
            make_cmd(PlaylistCmd.DeletePlaylist, playlist.id),
            PlaylistEvt.PlaylistDeleted,
        )

        resp = await self.client.delete(f"/api/playlists/{playlist.id}")
        self.assertEqual(204, resp.status)

    @unittest_run_loop
    async def test_delete_not_found(self):
        playlist_id = IdentityService.id_playlist()
        resp = await self.client.delete(f"/api/playlists/{playlist_id}")
        self.assertEqual(404, resp.status)
