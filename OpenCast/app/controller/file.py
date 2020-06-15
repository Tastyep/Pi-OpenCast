from .controller import Controller


class FileController(Controller):
    def __init__(self, app_facade, server):
        super().__init__(app_facade)
        self._server = server
        # Todo hardcoded port
        self._index_html = """
                                {{ project_name }} API.
                                Please visit :8081
                           """

        self._server.route("/", callback=self._index)

    def _index(self):
        return self._server.template(self._index_html, project_name="OpenCast")
