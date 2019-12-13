import os

from .controller import Controller


class FileController(Controller):
    def __init__(self, cmd_dispatcher, server, app_path):
        super(FileController, self).__init__(cmd_dispatcher)
        self._server = server
        self._static_path = os.path.join(app_path, 'static')

        server.add_template_path(os.path.join(app_path, 'views'))
        server.route('/', callback=self._remote)
        server.route('/remote', callback=self._remote)
        server.route('/static/<filepath:path>', callback=self._serve_file)

    def _remote(self):
        return self._server.template('remote')

    def _serve_file(self, filepath):
        return self._server.serve_file(filepath, self._static_path)
