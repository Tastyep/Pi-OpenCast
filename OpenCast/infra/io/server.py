""" High level HTTP server """

import structlog
from aiohttp import web
from aiohttp.abc import AbstractAccessLogger
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from aiohttp_middlewares import cors_middleware


class AccessLogger(AbstractAccessLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = structlog.get_logger(__name__)

    def log(self, request, response, time):
        self._logger.debug(
            f"{response.status}",
            method=request.method,
            path=request.path,
            duration=f"{0:.3f}s".format(time),
        )


class Server:
    def __init__(self, app):
        self._app = app
        self._app["websockets"] = []
        self._app.on_shutdown.append(self._on_shutdown)
        self._logger = structlog.get_logger(__name__)

    def route(self, method, route, handle):
        route = self._app.router.add_route(method, route, handle)

    def start(self, host, port):
        self._logger.info("Started", host=host, port=port)

        web.run_app(self._app, host=host, port=port, access_log_class=AccessLogger)

    def make_web_socket(self):
        ws = web.WebSocketResponse()
        self._app["websockets"].append(ws)
        return ws

    def make_json_response(self, status, body, dumps):
        return web.json_response(body, status=status, dumps=dumps)

    async def _on_shutdown(self, app):
        for ws in app["websockets"]:
            await ws.close(code=999, message="Server shutdown")


def make_server():
    app = web.Application(
        middlewares=[
            # Allow CORS requests for API url from all localhost urls
            cors_middleware(allow_all=True),
            validation_middleware,
        ]
    )
    setup_aiohttp_apispec(
        app=app,
        title="OpenCast Documentation",
        version="v1",
        url="/api/docs/swagger.json",
        swagger_path="/api/docs",
    )
    return Server(app)
