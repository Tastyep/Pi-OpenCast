import logging
import os

from bottle import (
    Bottle,
    response,
    run,
    template,
)


class Server(object):
    def __init__(self):
        self._server = Bottle()
        self._logger = logging.getLogger(__name__)

    def route(self, route, *args, **kwargs):
        self._server.route(route, *args, **kwargs)

    def run(self, host, port):
        self._logger.info("[server] started on {}:{}".format(host, port))

        run(
            self._server,
            host=host,
            port=port,
            reloader=False,
            debug=True,
            quiet=True
        )

    def enable_cors(self):
        def impl():
            response.headers['Access-Control-Allow-Origin'] = '*'

        self._server.add_hook('after_request', impl)

    def template(self, *args, **kwargs):
        return template(*args, **kwargs)
