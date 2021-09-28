""" Video capabilities monitoring routes """

import structlog
from aiohttp_apispec import docs

from OpenCast.app.command import video as Cmd
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model import Id
from OpenCast.domain.model.video import VideoSchema

from .monitor import MonitorController
from .monitoring_schema import Videos


class VideoMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "/videos")
        self._video_repo = data_facade.video_repo

        self._route("GET", "/", handle=self.list)
        self._route("GET", "/{id:" + self.UUID + "}", handle=self.get)
        self._route("DELETE", "/{id:" + self.UUID + "}", handle=self.delete)

    @docs(
        tags=["video"],
        summary="List videos",
        description="Retrieve a list of all videos in the system",
        operationId="listVideos",
        responses={
            200: {
                "description": "Successful operation",
                "schema": Videos,
            }
        },
    )
    async def list(self, req):
        videos = self._video_repo.list()
        return self._ok({"videos": videos})

    @docs(
        tags=["video"],
        summary="Get video",
        description="Querie and return a video by ID",
        operationId="getVideoById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the video to retrieve",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            200: {"description": "Successful operation", "schema": VideoSchema},
            404: {"description": "Video not found"},
        },
    )
    async def get(self, req):
        id = Id(req.match_info["id"])
        video = self._video_repo.get(id)
        if video is None:
            return self._not_found()
        return self._ok(video)

    @docs(
        tags=["video"],
        summary="Delete video",
        description="Remove a video by ID",
        operationId="deleteVideoById",
        parameters=[
            {
                "in": "path",
                "name": "id",
                "description": "ID of the video to remove",
                "type": "string",
                "required": True,
            }
        ],
        responses={
            204: {"description": "Successful operation"},
            404: {"description": "Video not found"},
        },
    )
    async def delete(self, req):
        id = Id(req.match_info["id"])
        if not self._video_repo.exists(id):
            return self._not_found()

        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            channel.send(self._no_content())

        self._observe_dispatch({VideoEvt.VideoDeleted: on_success}, Cmd.DeleteVideo, id)

        return await channel.receive()
