import structlog
from bottle import Bottle, HTTPResponse, request, response, run, template


class EnableCors(object):
    name = "enable_cors"
    api = 2

    _allow_origin = "*"
    _allow_methods = "PUT, GET, POST, DELETE, OPTIONS"
    _allow_headers = (
        "Authorization, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
    )

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers["Access-Control-Allow-Origin"] = self._allow_origin
            response.headers["Access-Control-Allow-Methods"] = self._allow_methods
            response.headers["Access-Control-Allow-Headers"] = self._allow_headers

            if request.method != "OPTIONS":
                # actual request; reply with the actual response
                return fn(request, *args, **kwargs)

        return _enable_cors


class Server:
    def __init__(self):
        self._server = Bottle()
        self._logger = structlog.get_logger(__name__)
        self._enable_cors()

    def route(self, route, *args, **kwargs):
        self._server.route(route, *args, **kwargs)

    def run(self, host, port):
        self._logger.info(f"Started", host=host, port=port)

        run(self._server, host=host, port=port, reloader=False, debug=True, quiet=True)

    def template(self, *args, **kwargs):
        return template(*args, **kwargs)

    def make_response(self, status, body):
        return HTTPResponse(body, status)

    def _enable_cors(self):
        def options_handler(path=None):
            return

        self._server.install(EnableCors())
        self._server.route("/", method="OPTIONS", callback=options_handler)
        self._server.route("/<path:path>", method="OPTIONS", callback=options_handler)
