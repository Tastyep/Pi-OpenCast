import functools
import json

from OpenCast.app.command import make_cmd
from OpenCast.app.tool.json_encoder import ModelEncoder

from .controller import Controller


class MonitorController(Controller):
    def __init__(self, app_facade, infra_facade, base_route):
        super().__init__(app_facade)
        self._server = infra_facade.server
        self._base_route = f"/api{base_route}"
        self._json_dumps = functools.partial(json.dumps, cls=ModelEncoder)

    def _observe_dispatch(
        self, evtcls_handler: dict, cmd_cls, component_id, *args, **kwargs
    ):
        cmd = make_cmd(cmd_cls, component_id, *args, **kwargs)
        self._evt_dispatcher.observe(cmd.id, evtcls_handler, 1)
        self._cmd_dispatcher.dispatch(cmd)

    def _route(self, method, route, handle):
        self._server.route(method, f"{self._base_route}{route}", handle)

    def _ok(self, body=None):
        return self._make_response(200, body)

    def _bad_request(self):
        return self._make_response(400, None)

    def _make_response(self, status, body):
        return self._server.make_json_response(status, body, self._json_dumps)
