from .controller import Controller


class MonitorController(Controller):
    def __init__(self, app_facade, infra_facade):
        super().__init__(app_facade)
        self._server = infra_facade.server

    def _route(self, url, *args, **kwargs):
        self._server.route(f"/api/{url}", *args, **kwargs)
