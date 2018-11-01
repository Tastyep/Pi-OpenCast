#!/usr/bin/env python

import sys
import logging
import os

import video_controller as controller

from bottle import Bottle, SimpleTemplate, request, response, \
                   template, run, static_file, TEMPLATE_PATH


logger = logging.getLogger("App")
app = Bottle()
SimpleTemplate.defaults["get_url"] = app.get_url
app_path = os.path.dirname(os.path.realpath(__file__))


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
    elif control == "next":
        controller.next_video()
    elif control == "right":
        controller.seek_time(True, False)
    elif control == "left":
        controller.seek_time(False, False)
    elif control == "longright":
        controller.seek_time(True, True)
    elif control == "longleft":
        controller.seek_time(False, True)
    return "1"


@app.route('/sound')
def sound():
    vol = request.query['vol']
    controller.change_volume(vol == "more")
    return "1"


@app.route('/running')
def webstate():
    return 0


def main():
    logging.basicConfig(
        filename='RaspberryCast.log',
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt='%m-%d %H:%M:%S',
        level=logging.DEBUG
    )

    # Creating handler to print messages on stdout
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    TEMPLATE_PATH.insert(0, os.path.join(app_path, 'views'))

    run(app, reloader=False, host='0.0.0.0', debug=True, quiet=True, port=2020)


if __name__ == '__main__':
    main()
