""" High level HTTP server """

import structlog
from aiohttp import web
from aiohttp_middlewares import cors_middleware


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

        web.run_app(self._app, host=host, port=port)

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
    return Server(
        web.Application(
            middlewares=[
                # Allow CORS requests for API url from all localhost urls
                cors_middleware(allow_all=True),
            ]
        )
    )
