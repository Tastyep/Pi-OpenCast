from aiohttp.test_utils import unittest_run_loop

from OpenCast.app.command import make_cmd
from OpenCast.app.command import playlist as PlaylistCmd
from OpenCast.app.command import video as VideoCmd
from OpenCast.app.service.error import OperationError
from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase, asyncio


class PlaylistMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super(PlaylistMonitorControllerTest, self).setUp()
        self.playlist_id = IdentityService.id_playlist()
        self.data_producer.playlist(self.playlist_id, "playlist1").video(
            "source1"
        ).video("source2").playlist(
            IdentityService.id_playlist(), "playlist2"
        ).populate(
            self.data_facade
        )

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
        self.error_on(PlaylistCmd.CreatePlaylist, "Error message")
        resp = await self.client.post("/api/playlists/", json={"name": "test_playlist"})
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
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
        playlist = self.playlist_repo.get(self.playlist_id)
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
        playlist = self.playlist_repo.get(self.playlist_id)
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
        playlist = self.playlist_repo.get(self.playlist_id)
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
        playlist = self.playlist_repo.get(self.playlist_id)

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
        playlist = self.playlist_repo.get(self.playlist_id)
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
                    "args": {"error": "Error message"},
                },
            ]
        )

        resp = await self.client.patch(f"/api/playlists/{playlist.id}", json=req_body)
        body = await resp.json()
        self.assertEqual(500, resp.status)
        self.assertEqual(
            {
                "message": "Error message",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_delete(self):
        playlist = self.playlist_repo.get(self.playlist_id)
        self.queueing_service.queue.return_value = []  # Ignore the queueing action
        self.expect_and_raise(
            make_cmd(PlaylistCmd.DeletePlaylist, playlist.id),
            [
                {
                    "type": PlaylistEvt.PlaylistDeleted,
                    "args": {"name": playlist.name, "ids": playlist.ids},
                }
            ],
        )

        resp = await self.client.delete(f"/api/playlists/{playlist.id}")
        self.assertEqual(204, resp.status)

    @unittest_run_loop
    async def test_delete_not_found(self):
        playlist_id = IdentityService.id_playlist()
        resp = await self.client.delete(f"/api/playlists/{playlist_id}")
        self.assertEqual(404, resp.status)

    @unittest_run_loop
    async def test_delete_forbidden(self):
        resp = await self.client.delete(f"/api/playlists/{HOME_PLAYLIST.id}")
        body = await resp.json()

        self.assertEqual(403, resp.status)
        self.assertEqual(
            {
                "message": f"{HOME_PLAYLIST.name} playlist can't be deleted",
                "details": {},
            },
            body,
        )

    @unittest_run_loop
    async def test_event_listening(self):
        async with self.client.ws_connect("/api/playlists/events") as ws:
            playlist = self.playlist_repo.get(self.playlist_id)
            cmd_id = IdentityService.id_command(PlaylistCmd.CreatePlaylist, playlist.id)
            created_evt = PlaylistEvt.PlaylistCreated(
                cmd_id,
                playlist.id,
                "name",
                [],
            )
            self.evt_dispatcher.dispatch(created_evt)
            await self.expect_ws_events(ws, [created_evt])

            cmd_id = IdentityService.id_command(
                PlaylistCmd.UpdatePlaylistContent, playlist.id
            )
            second_evt = PlaylistEvt.PlaylistContentUpdated(cmd_id, playlist.id, [])
            self.evt_dispatcher.dispatch(created_evt)
            self.evt_dispatcher.dispatch(second_evt)
            await self.expect_ws_events(ws, [created_evt, second_evt])

    @unittest_run_loop
    async def test_invalid_event_listening(self):
        async with self.client.ws_connect("/api/player/events") as ws:
            video_id = IdentityService.id_video("source")
            cmd_id = IdentityService.id_command(VideoCmd.CreateVideo, video_id)
            video_evt = VideoEvt.VideoCreated(
                cmd_id,
                video_id,
                "source",
                IdentityService.random(),
                "album",
                "title",
                "http",
                "thumbnail",
            )
            self.evt_dispatcher.dispatch(video_evt)
            with self.assertRaises(asyncio.TimeoutError):
                await self.expect_ws_events(ws, [video_evt])
