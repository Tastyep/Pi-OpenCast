import logging
import os

from bottle import request

from OpenCast.config import config

from ..command.player_commands import *
from .controller import Controller

logger = logging.getLogger(__name__)


class PlayerController(Controller):
    def __init__(self, cmd_dispatcher, server):
        super(PlayerController, self).__init__(cmd_dispatcher)

        server.route('/stream', callback=self._stream)
        server.route('/queue', callback=self._queue)
        server.route('/video', callback=self._video)
        server.route('/subtitle', callback=self._subtitle)
        server.route('/sound', callback=self._sound)
        server.route('/running', callback=self._running)

    def _stream(self):
        cmd = PlayVideo(request.query['url'])
        self._cmd_dispatcher.dispatch(cmd)
        return '1'

    def _queue(self):
        cmd = QueueVideo(request.query['url'])
        self._cmd_dispatcher.dispatch(cmd)

    def _video(self):
        control = request.query['control']
        cmd = None

        logger.debug("Control command received: {}".format(control))
        if control == 'pause':
            cmd = ToggleVideoState()
        elif control == 'stop':
            cmd = StopVideo()
        elif control == 'right':
            cmd = SeekVideo(30)
        elif control == 'left':
            cmd = SeekVideo(-30)
        elif control == 'longright':
            cmd = SeekVideo(300)
        elif control == 'longleft':
            cmd = SeekVideo(-300)
        elif control == 'prev':
            cmd = PrevVideo()
        elif control == 'next':
            cmd = NextVideo()
        else:
            return '0'

        self._cmd_dispatcher.dispatch(cmd)
        return '1'

    def _sound(self):
        cmd = None
        if request.query['vol'] == 'more':
            cmd = IncreaseVolume(0.1)
        else:
            cmd = DecreaseVolume(0.1)

        self._cmd_dispatcher.dispatch(cmd)
        return '1'

    def _subtitle(self):
        action = request.query['action']

        logger.debug("Subtitle command received: {}".format(action))
        if action == 'toggle':
            self._cmd_dispatcher.dispatch(cmd)
        elif action == 'increase':
            self._cmd_dispatcher.dispatch(cmdTrue)
        elif action == 'decrease':
            self._cmd_dispatcher.dispatch(cmdFalse)

    def _running(self):
        return 1
