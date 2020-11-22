""" Playlist capabilities monitoring routes """

import structlog
from aiohttp_apispec import docs, json_schema
from marshmallow import fields

from OpenCast.app.command import playlist as Cmd
from OpenCast.app.service.error import OperationError
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.model import Id
from OpenCast.domain.model.playlist import PlaylistSchema
from OpenCast.domain.service.identity import IdentityService

from .monitor import MonitorController
from .monitoring_schema import Videos, schema


class PlaylistMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "/playlists")
        self._playlist_repo = data_facade.playlist_repo
        self._video_repo = data_facade.video_repo

        self._route("POST", "/", handle=self.create)
        self._route("GET", "/", handle=self.list)
        self._route("GET", "/{id:" + self.UUID + "}", handle=self.get)
        self._route("GET", "/{id:" + self.UUID + "}/videos", handle=self.list_videos)
        self._route("PATCH", "/{id:" + self.UUID + "}", handle=self.update)
        self._route("DELETE", "/{id:" + self.UUID + "}", handle=self.delete)

    @docs(
        tags=["playlist"],
        summary="Add playlist",
        description="Add a new playlist",
        operationId="addPlaylist",
        responses={
            200: {"description": "Ok. Playlist created", "schema": PlaylistSchema},
            422: {"description": "Validation error"},
        },
    )
    @json_schema(
        schema(
            PlaylistMeta={
                "name": fields.String(),
                "ids": [fields.UUID()],
            }
        )
    )
    async def create(self, req):
        data = await req.json()
        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            playlist = self._playlist_repo.get(evt.model_id)
            channel.send(self._ok(playlist))

        def on_error(evt):
            channel.send(self._bad_request(evt.error))

        self._observe_dispatch(
            {PlaylistEvt.PlaylistCreated: on_success, OperationError: on_error},
            Cmd.CreatePlaylist,
            IdentityService.id_playlist(),
            **data,
        )

        return await channel.receive()

    @docs(
        tags=["playlist"],
        summary="List playlists",
        description="Retrieve a list of all playlists in the system",
        operationId="listPlaylists",
        responses={
            200: {
                "description": "Successful operation",
                "schema": schema(Playlists={"playlists": [PlaylistSchema]}),
            }
        },
    )
    async def list(self, req):
        playlists = self._playlist_repo.list()
        return self._ok(playlists)

    @docs(
        tags=["playlist"],
        summary="Get playlist",
        description="Querie and return a playlist by ID",
        operationId="getPlaylistById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the playlist to retrieve",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            200: {"description": "Successful operation", "schema": PlaylistSchema},
            404: {"description": "Playlist not found"},
        },
    )
    async def get(self, req):
        id = Id(req.match_info["id"])
        playlist = self._playlist_repo.get(id)
        if playlist is None:
            return self._not_found()
        return self._ok(playlist)

    @docs(
        tags=["playlist", "video"],
        summary="List playlist videos",
        description="Retrieve the videos contained by the playlist",
        operationId="listPlaylistVideos",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the playlist to list videos from",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            200: {
                "description": "Successful operation",
                "schema": Videos,
            },
            404: {"description": "Playlist not found"},
        },
    )
    async def list_videos(self, req):
        id = Id(req.match_info["id"])
        playlist = self._playlist_repo.get(id)
        if playlist is None:
            return self._not_found()

        videos = self._video_repo.list(playlist.ids)
        return self._ok(videos)

    @docs(
        tags=["playlist"],
        summary="Update playlist",
        description="Update a playlist by ID",
        operationId="updatePlaylist",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the playlist to update",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            200: {"description": "Ok. Playlist updated", "schema": PlaylistSchema},
            404: {"description": "Playlist not found"},
            422: {"description": "Validation error"},
        },
    )
    @json_schema(
        schema(
            PlaylistUpdate={
                "name": fields.String(),
                "ids": [fields.UUID()],
            }
        )
    )
    async def update(self, req):
        id = Id(req.match_info["id"])
        if not self._playlist_repo.exists(id):
            return self._not_found()

        data = await req.json()
        field_count = len(data)
        success_count = 0
        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            nonlocal success_count
            success_count += 1
            if success_count == field_count:
                playlist = self._playlist_repo.get(evt.model_id)
                channel.send(self._ok(playlist))

        def on_error(evt):
            channel.send(self._bad_request(evt.error))

        def update_field(field, cmd_cls, evt_cls):
            self._observe_dispatch(
                {
                    evt_cls: on_success,
                    OperationError: on_error,
                },
                cmd_cls,
                id,
                data[field],
            )

        for field in data:
            if field == "name":
                update_field(field, Cmd.RenamePlaylist, PlaylistEvt.PlaylistRenamed)
            elif field == "ids":
                update_field(
                    field, Cmd.UpdatePlaylistContent, PlaylistEvt.PlaylistContentUpdated
                )

        return await channel.receive()

    @docs(
        tags=["playlist"],
        summary="Delete playlist",
        description="Remove a playlist by ID",
        operationId="deletePlaylistById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the playlist to remove",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            204: {"description": "Successful operation"},
            404: {"description": "Playlist not found"},
        },
    )
    async def delete(self, req):
        id = Id(req.match_info["id"])
        if not self._playlist_repo.exists(id):
            return self._not_found()

        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            channel.send(self._no_content())

        self._observe_dispatch(
            {PlaylistEvt.PlaylistDeleted: on_success}, Cmd.DeletePlaylist, id
        )

        return await channel.receive()
