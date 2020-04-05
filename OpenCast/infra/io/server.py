import logging

from bottle import Bottle, request, response, run, template


class EnableCors:
    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
            response.headers[
                "Access-Control-Allow-Headers"
            ] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"

            if request.method != "OPTIONS":
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors


class Server:
    def __init__(self):
        self._server = Bottle()
        self._server.install(EnableCors())
        self._logger = logging.getLogger(__name__)

    def route(self, route, *args, **kwargs):
        self._server.route(route, *args, **kwargs)

    def run(self, host, port):
        self._logger.info(f"[server] started on {host}:{port}")

        run(self._server, host=host, port=port, reloader=False, debug=True, quiet=True)

    def template(self, *args, **kwargs):
        return template(*args, **kwargs)
