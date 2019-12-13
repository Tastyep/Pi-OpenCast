import logging
import os
from mimetypes import guess_type

from bottle import (
    TEMPLATE_PATH,
    Bottle,
    SimpleTemplate,
    response,
    run,
    static_file,
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

    def serve_file(self, filename, root):
        fullpath = os.path.join(root, filename)
        mimetype = guess_type(fullpath)[0]
        return static_file(filename, root=root, mimetype=mimetype)

    def add_template_path(self, path):
        TEMPLATE_PATH.insert(0, path)

    def template(self, file):
        return template(file)
