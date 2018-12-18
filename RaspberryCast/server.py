import logging
import os

from bottle import (
    Bottle,
    SimpleTemplate,
    request,
    response,
    template,
    run,
    static_file,
    TEMPLATE_PATH,
)

from . import config
from . import video_controller

logger = logging.getLogger(__name__)
app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class Server(object):
    def __init__(self):
        self._app = Bottle()
        self._controller = video_controller.make_video_controller()

        TEMPLATE_PATH.insert(0, os.path.join(app_path, 'views'))
        SimpleTemplate.defaults['get_url'] = self._app.get_url

    def run(self):
        serverConfig = config.config['Server']

        self._set_routes()
        logger.info("[server] started on {}:{}".format(serverConfig.host, serverConfig.port))
        run(self._app, host=serverConfig.host, port=serverConfig.port,
            reloader=False, debug=True, quiet=True)

    def _set_routes(self):
        self._app.route('/static/<filename>', name='static',
                        callback=self._serve_file)
        self._app.route('/', callback=self._remote)
        self._app.route('/remote', callback=self._remote)
        self._app.route('/stream', callback=self._stream)
        self._app.route('/queue', callback=self._queue)
        self._app.route('/video', callback=self._video)
        self._app.route('/sound', callback=self._sound)
        self._app.route('/running', callback=self._running)

        self._app.add_hook('after_request', self._enable_cors)

    def _serve_file(self, filename):
        return static_file(filename, root=os.path.join(app_path, 'static'))

    def _remote(self):
        return template('remote')

    def _stream(self):
        url = request.query['url']
        self._controller.stream_video(url)
        return '1'

    def _queue(self):
        url = request.query['url']
        self._controller.queue_video(url)

    def _video(self):
        control = request.query['control']
        logger.debug("Control command received: {}".format(control))

        if control == 'pause':
            self._controller.play_pause_video(True)
        elif control == 'stop':
            self._controller.stop_video()
        elif control == 'right':
            self._controller.seek_time(True, False)
        elif control == 'left':
            self._controller.seek_time(False, False)
        elif control == 'longright':
            self._controller.seek_time(True, True)
        elif control == 'longleft':
            self._controller.seek_time(False, True)
        elif control == 'prev':
            self._controller.prev_video()
        elif control == 'next':
            self._controller.next_video()
        return '1'

    def _sound(self):
        vol = request.query['vol']
        self._controller.change_volume(vol == 'more')
        return '1'

    def _running(self):
        return 1

    def _enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
