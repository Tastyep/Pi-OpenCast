""" Application monitoring routes """

import asyncio

import structlog
from aiohttp_apispec import docs

from OpenCast.app.controller.monitor import MonitorController
from OpenCast.app.notification import Notification
from OpenCast.domain.event import album as AlbumEvt
from OpenCast.domain.event import artist as ArtistEvt
from OpenCast.domain.event import player as PlayerEvt
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.infra.event.downloader import DownloadInfo


class RootMonitController(MonitorController):
    """The controller in charge of application related requests"""

    def __init__(self, app_facade, infra_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "")

        self._route("GET", "/events", self.stream_events)

    @docs(
        tags=["events"],
        summary="Stream application events",
        description="Stream application events over WebSocket",
        operationId="streamAppEvents",
    )
    async def stream_events(self, request):
        ws = self._server.make_web_socket()
        await ws.prepare(request)
        self._logger.debug("websocket created")

        channel = self._io_factory.make_janus_channel()

        def handler_factory(_):
            return channel.send

        self._observe(PlayerEvt, handler_factory)
        self._observe(PlaylistEvt, handler_factory)
        self._observe(VideoEvt, handler_factory)
        self._observe(AlbumEvt, handler_factory)
        self._observe(ArtistEvt, handler_factory)
        self._evt_dispatcher.observe({DownloadInfo: channel.send})
        self._evt_dispatcher.observe({Notification: channel.send})

        while True:
            event = await channel.receive()
            await self._send_ws_event(ws, event)
            channel.task_done()

    async def _send_ws_event(self, ws, event):
        event_name = type(event).__name__
        try:
            return await ws.send_json(
                {"name": event_name, "event": event}, dumps=self._event_dumps
            )
        except RuntimeError as e:
            self._logger.error("websocket transfer error", event=event, error=e)
            return await asyncio.wait_for(ws.close(), timeout=self.WS_CLOSE_TIMEOUT)
