""" Album capabilities monitoring routes """

import structlog
from aiohttp_apispec import docs

import OpenCast.app.command.album as Cmd
import OpenCast.domain.event.album as AlbumEvt
from OpenCast.app.controller.monitor import MonitorController
from OpenCast.app.controller.monitoring_schema import schema
from OpenCast.domain.model import Id
from OpenCast.domain.model.album import AlbumSchema


class AlbumMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "/albums")
        self._album_repo = data_facade.album_repo

        self._route("GET", "/", handle=self.list)
        self._route("GET", "/{id:" + self.UUID + "}", handle=self.get)
        self._route("DELETE", "/{id:" + self.UUID + "}", handle=self.delete)

    @docs(
        tags=["album"],
        summary="List albums",
        description="Retrieve a list of all albums in the system",
        operationId="listAlbums",
        responses={
            200: {
                "description": "Successful operation",
                "schema": schema(Albums={"albums": [AlbumSchema]}),
            }
        },
    )
    async def list(self, _):
        albums = self._album_repo.list()
        return self._ok({"albums": albums})

    @docs(
        tags=["album"],
        summary="Get album",
        description="Query and return an album by ID",
        operationId="getAlbumById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the album to retrieve",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            200: {"description": "Successful operation", "schema": AlbumSchema},
            404: {"description": "Album not found"},
        },
    )
    async def get(self, req):
        id = Id(req.match_info["id"])
        album = self._album_repo.get(id)
        if album is None:
            return self._not_found()
        return self._ok(album)

    @docs(
        tags=["album"],
        summary="Delete album",
        description="Remove an album by ID",
        operationId="deleteAlbumById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the album to remove",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            204: {"description": "Successful operation"},
            404: {"description": "Album not found"},
        },
    )
    async def delete(self, req):
        id = Id(req.match_info["id"])
        if not self._album_repo.exists(id):
            return self._not_found()

        channel = self._io_factory.make_janus_channel()

        def on_success(_):
            channel.send(self._no_content())

        self._observe_dispatch(
            {AlbumEvt.AlbumDeleted: on_success},
            Cmd.DeleteAlbum,
            id,
        )

        return await channel.receive()
