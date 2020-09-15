""" Abstraction of a monitoring controller """

import asyncio
import functools
import json

from OpenCast.app.command import make_cmd
from OpenCast.app.tool.json_encoder import EventEncoder, ModelEncoder

from .controller import Controller


class MonitorController(Controller):
    WS_CLOSE_TIMEOUT = 5.0
    UUID = "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"

    def __init__(self, logger, app_facade, infra_facade, base_route):
        super().__init__(logger, app_facade)
        self._server = infra_facade.server
        self._io_factory = infra_facade.io_factory
        self._base_route = f"/api{base_route}"
        self._model_dumps = functools.partial(json.dumps, cls=ModelEncoder)
        self._event_dumps = functools.partial(json.dumps, cls=EventEncoder)

    def _observe_dispatch(
        self, evtcls_handler: dict, cmd_cls, component_id, *args, **kwargs
    ):
        cmd = make_cmd(cmd_cls, component_id, *args, **kwargs)
        self._evt_dispatcher.observe_result(cmd.id, evtcls_handler, 1)
        self._cmd_dispatcher.dispatch(cmd)

    def _route(self, method, route, handle):
        self._server.route(method, f"{self._base_route}{route}", handle)

    def _ok(self, body=None):
        return self._make_response(200, body)

    def _no_content(self):
        return self._make_response(204, None)

    def _bad_request(self):
        return self._make_response(400, None)

    def _not_found(self):
        return self._make_response(404, None)

    def _make_response(self, status, body):
        return self._server.make_json_response(status, body, self._model_dumps)

    async def run_web_socket(self, request):
        ws = self._server.make_web_socket()
        await ws.prepare(request)
        return ws

    async def _send_ws_event(self, ws, event):
        event_name = type(event).__name__
        try:
            return await ws.send_json(
                {"name": event_name, "event": event}, dumps=self._event_dumps
            )
        except RuntimeError as e:
            self._logger.error("websocket transfer error", event=event, error=e)
            return await asyncio.wait_for(ws.close(), timeout=self.WS_CLOSE_TIMEOUT)
