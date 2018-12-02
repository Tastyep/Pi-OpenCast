#!/usr/bin/env python3

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

from . import video_controller


app = Bottle()
logger = logging.getLogger(__name__)
app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
controller = video_controller.make_video_controller()


@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'


@app.route('/static/<filename>', name='static')
def server_static(filename):
    return static_file(filename, root=os.path.join(app_path, 'static'))


@app.route('/')
@app.route('/remote')
def remote():
    return template('remote')


@app.route('/stream')
def stream():
    url = request.query['url']
    controller.stream_video(url)
    return "1"


@app.route('/queue')
def queue():
    url = request.query['url']
    controller.queue_video(url)


@app.route('/video')
def video():
    control = request.query['control']
    logger.debug("Control command received: " + control)

    if control == "pause":
        controller.play_pause_video(True)
    elif control == "stop":
        controller.stop_video()
    elif control == "right":
        controller.seek_time(True, False)
    elif control == "left":
        controller.seek_time(False, False)
    elif control == "longright":
        controller.seek_time(True, True)
    elif control == "longleft":
        controller.seek_time(False, True)
    elif control == "prev":
        controller.prev_video()
    elif control == "next":
        controller.next_video()
    return "1"


@app.route('/sound')
def sound():
    vol = request.query['vol']
    controller.change_volume(vol == "more")
    return "1"


@app.route('/running')
def webstate():
    return 0


def make_logger():
    path = os.path.join(app_path, 'RaspberryCast.log')
    return logging.FileHandler(path)


def run_server():
    logger.info('[server] started')
    TEMPLATE_PATH.insert(0, os.path.join(app_path, 'views'))
    SimpleTemplate.defaults["get_url"] = app.get_url
    run(app, reloader=False, host='0.0.0.0', debug=True, quiet=True, port=2020)
