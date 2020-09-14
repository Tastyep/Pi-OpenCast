""" Video capabilities monitoring routes """

import structlog
from OpenCast.app.command import video as Cmd
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model import Id

from .monitor import MonitorController


class VideoMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "/videos")
        self._video_repo = data_facade.video_repo

        self._route("GET", "/", handle=self.list)
        self._route("GET", "/{id}", handle=self.get)
        self._route("DELETE", "/{id}", handle=self.delete)
        self._route("GET", "/events", self.stream_events)

    async def list(self, req):
        videos = self._video_repo.list()
        return self._ok(videos)

    async def get(self, req):
        id = Id(req.match_info["id"])
        video = self._video_repo.get(id)
        if video is None:
            return self._not_found()
        return self._ok(video)

    async def delete(self, req):
        id = Id(req.match_info["id"])
        if not self._video_repo.exists(id):
            return self._not_found()

        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            channel.send(self._no_content())

        self._observe_dispatch({VideoEvt.VideoDeleted: on_success}, Cmd.DeleteVideo, id)

        return await channel.receive()

    async def stream_events(self, request):
        ws = await self.run_web_socket(request)
        channel = self._io_factory.make_janus_channel()
        self._logger.debug("video websocket created")

        def handler_factory(_):
            return channel.send

        self._observe(VideoEvt, handler_factory)

        while True:
            event = await channel.receive()
            await self._send_ws_event(ws, event)

        # TODO: cleanup websocket
        return ws
