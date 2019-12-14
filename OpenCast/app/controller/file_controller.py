import os

from .controller import Controller


class FileController(Controller):
    def __init__(self, cmd_dispatcher, server):
        super(FileController, self).__init__(cmd_dispatcher)
        self._server = server
        # Todo hardcoded port
        self._index_html = '''
                                {{ project_name }} API.
                                Please visit :8081
                           '''

        server.route('/', callback=self._index)

    def _index(self):
        return self._server.template(self._index_html, project_name='OpenCast')
