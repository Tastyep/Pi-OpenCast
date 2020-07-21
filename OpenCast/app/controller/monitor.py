import json

from OpenCast.app.tool.json_encoder import ModelEncoder

from .controller import Controller


class MonitorController(Controller):
    def __init__(self, app_facade, infra_facade, base_route):
        super().__init__(app_facade)
        self._server = infra_facade.server
        self._base_route = f"/api{base_route}"
        self._json_dumps = functools.partial(json.dumps, cls=ModelEncoder)

    def _route(self, route, *args, **kwargs):
        self._server.route(f"{self._base_route}{route}", *args, **kwargs)

    def _make_response(self, status, body):
        return self._server.make_json_response(status, body, self._json_dumps)
