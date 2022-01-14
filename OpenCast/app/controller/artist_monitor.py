""" Artist capabilities monitoring routes """

import structlog
from aiohttp_apispec import docs

import OpenCast.app.command.artist as Cmd
import OpenCast.domain.event.artist as ArtistEvt
from OpenCast.app.controller.monitor import MonitorController
from OpenCast.app.controller.monitoring_schema import schema
from OpenCast.domain.model import Id
from OpenCast.domain.model.artist import ArtistSchema


class ArtistMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "/artists")
        self._artist_repo = data_facade.artist_repo

        self._route("GET", "/", handle=self.list)
        self._route("GET", "/{id:" + self.UUID + "}", handle=self.get)
        self._route("DELETE", "/{id:" + self.UUID + "}", handle=self.delete)

    @docs(
        tags=["artist"],
        summary="List artists",
        description="Retrieve a list of all artists in the system",
        operationId="listArtists",
        responses={
            200: {
                "description": "Successful operation",
                "schema": schema(Artists={"artists": [ArtistSchema]}),
            }
        },
    )
    async def list(self, _):
        artists = self._artist_repo.list()
        return self._ok({"artists": artists})

    @docs(
        tags=["artist"],
        summary="Get artist",
        description="Query and return an artist by ID",
        operationId="getArtistById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the artist to retrieve",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            200: {"description": "Successful operation", "schema": ArtistSchema},
            404: {"description": "Artist not found"},
        },
    )
    async def get(self, req):
        id = Id(req.match_info["id"])
        artist = self._artist_repo.get(id)
        if artist is None:
            return self._not_found()
        return self._ok(artist)

    @docs(
        tags=["artist"],
        summary="Delete artist",
        description="Remove an artist by ID",
        operationId="deleteArtistById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the artist to remove",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            204: {"description": "Successful operation"},
            404: {"description": "Artist not found"},
        },
    )
    async def delete(self, req):
        id = Id(req.match_info["id"])
        if not self._artist_repo.exists(id):
            return self._not_found()

        channel = self._io_factory.make_janus_channel()

        def on_success(_):
            channel.send(self._no_content())

        self._observe_dispatch(
            {ArtistEvt.ArtistDeleted: on_success},
            Cmd.DeleteArtist,
            id,
        )

        return await channel.receive()
