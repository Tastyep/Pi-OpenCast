from OpenCast.app.command import make_cmd
from OpenCast.app.command import playlist as Cmd
from OpenCast.app.controller.playlist_monitor import PlaylistMonitController
from OpenCast.app.service.error import OperationError
from OpenCast.domain.event import playlist as Evt
from OpenCast.domain.service.identity import IdentityService

from .util import MonitorControllerTestCase


class PlaylistMonitorControllerTest(MonitorControllerTestCase):
    def setUp(self):
        super().setUp()

        self.data_producer.playlist("playlist1").video("source1").video(
            "source2"
        ).playlist("playlist2").populate(self.data_facade)

        self.playlist_repo = self.data_facade.playlist_repo
        self.video_repo = self.data_facade.video_repo
        self.playlists = self.playlist_repo.list()
        self.controller = PlaylistMonitController(
            self.app_facade, self.infra_facade, self.data_facade
        )

    def update_playlist(self, **kwargs):
        self.data_producer.playlist(**kwargs).populate(self.data_facade)

    async def test_list(self):
        req = self.make_request("GET", "/")
        resp = await self.route(self.controller.list, req)
        self.assertEqual(resp, (200, self.playlists))

    async def test_get(self):
        playlist_id = self.playlists[0].id
        req = self.make_request("GET", f"/{playlist_id}", {"id": str(playlist_id)})
        resp = await self.route(self.controller.get, req)
        self.assertEqual(resp, (200, self.playlists[0]))

    async def test_get_not_found(self):
        playlist_id = IdentityService.id_playlist()
        req = self.make_request("GET", f"/{playlist_id}", {"id": str(playlist_id)})
        resp = await self.route(self.controller.get, req)
        self.assertEqual(resp, (404, None))

    async def test_create(self):
        req = self.make_request("POST", "/")
        body = {"name": "test_playlist"}

        async def json_body():
            return body

        req.json = json_body
        playlist_id = None

        def make_and_respond(cmd):
            nonlocal playlist_id

            playlist_id = cmd.model_id
            self.data_producer.playlist(id=playlist_id, **body).populate(
                self.data_facade
            )
            self.app_facade.evt_dispatcher.dispatch(
                Evt.PlaylistCreated(cmd.id, playlist_id, cmd.name, cmd.ids)
            )

        self.hook_cmd(Cmd.CreatePlaylist, make_and_respond)
        resp = await self.route(self.controller.create, req)
        self.assertEqual(resp, (200, self.playlist_repo.get(playlist_id)))

    async def test_create_validation_error(self):
        req = self.make_request("POST", "/")
        body = {"namefdg": "test_playlist"}

        async def json_body():
            return body

        req.json = json_body

        resp = await self.route(self.controller.create, req)
        self.assertEqual(
            resp,
            (
                400,
                {
                    "error": {
                        "detail": {"namefdg": ["Unknown field."]},
                        "message": "Schema validation error.",
                    }
                },
            ),
        )

    async def test_create_service_error(self):
        req = self.make_request("POST", "/")
        body = {"name": "test_playlist"}

        async def json_body():
            return body

        req.json = json_body

        self.error_on(Cmd.CreatePlaylist, "Error message.")
        resp = await self.route(self.controller.create, req)
        self.assertEqual(
            resp,
            (
                400,
                {
                    "error": {
                        "detail": None,
                        "message": "Error message.",
                    }
                },
            ),
        )

    async def test_update(self):
        playlist_id = self.playlists[0].id
        req = self.make_request("PATCH", f"/{playlist_id}", {"id": str(playlist_id)})
        body = {"name": "test_playlist", "ids": [IdentityService.id_video("source3")]}

        async def json_body():
            return body

        req.json = json_body

        self.check_and_raise_l(
            [
                {
                    "cmd": make_cmd(Cmd.RenamePlaylist, playlist_id, body["name"]),
                    "hook": lambda cmd: self.update_playlist(
                        id=cmd.model_id, name=cmd.name
                    ),
                    "evt": Evt.PlaylistRenamed,
                    "args": {"name": body["name"]},
                },
                {
                    "cmd": make_cmd(
                        Cmd.UpdatePlaylistContent, playlist_id, body["ids"]
                    ),
                    "hook": lambda cmd: self.update_playlist(
                        id=cmd.model_id, ids=cmd.ids
                    ),
                    "evt": Evt.PlaylistContentUpdated,
                    "args": {"ids": body["ids"]},
                },
            ]
        )

        resp = await self.route(self.controller.update, req)
        self.assertEqual(
            resp,
            (200, self.playlist_repo.get(playlist_id)),
        )

    async def test_update_error(self):
        playlist_id = self.playlists[0].id
        req = self.make_request("PATCH", f"/{playlist_id}", {"id": str(playlist_id)})
        body = {"name": "test_playlist", "ids": [IdentityService.id_video("source3")]}

        async def json_body():
            return body

        req.json = json_body

        self.check_and_raise_l(
            [
                {
                    "cmd": make_cmd(Cmd.RenamePlaylist, playlist_id, body["name"]),
                    "hook": lambda cmd: self.update_playlist(
                        id=cmd.model_id, name=cmd.name
                    ),
                    "evt": Evt.PlaylistRenamed,
                    "args": {"name": body["name"]},
                },
                {
                    "cmd": make_cmd(
                        Cmd.UpdatePlaylistContent, playlist_id, body["ids"]
                    ),
                    "evt": OperationError,
                    "args": {"error": "Error message."},
                },
            ]
        )

        resp = await self.route(self.controller.update, req)
        self.assertEqual(
            resp,
            (
                400,
                {
                    "error": {
                        "detail": None,
                        "message": "Error message.",
                    }
                },
            ),
        )

    async def test_delete(self):
        playlist_id = self.playlists[0].id
        req = self.make_request("DELETE", f"/{playlist_id}", {"id": str(playlist_id)})
        self.check_and_raise(
            make_cmd(Cmd.DeletePlaylist, playlist_id), Evt.PlaylistDeleted
        )

        resp = await self.route(self.controller.delete, req)
        self.assertEqual(resp, (204, None))

    async def test_delete_not_found(self):
        playlist_id = IdentityService.id_playlist()
        req = self.make_request("DELETE", f"/{playlist_id}", {"id": str(playlist_id)})

        resp = await self.route(self.controller.delete, req)
        self.assertEqual(resp, (404, None))

    async def test_list_videos(self):
        playlist_id = self.playlists[0].id
        req = self.make_request(
            "GET", f"/{playlist_id}/videos", {"id": str(playlist_id)}
        )
        resp = await self.route(self.controller.list_videos, req)
        self.assertEqual(resp, (200, self.video_repo.list(self.playlists[0].ids)))
