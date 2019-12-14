import sys
import os
import yaml
import logging
import logging.config

from .config import config
from .infra.io.server import Server
from .infra.io import video_downloader
from .infra.media import player_wrapper

from .app.app_facade import AppFacade
from .app.controller.module import ControllerModule
from .app.service.module import ServiceModule


def _real_main(argv):
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    with open('{}/logging.yml'.format(app_path), 'r') as file:
        cfg = yaml.load(file, Loader=yaml.Loader)
        logging.config.dictConfig(cfg)
    logger = logging.getLogger(__name__)

    config.load_from_file('{}/config.ini'.format(app_path))
    serverConfig = config['Server']

    app_facade = AppFacade()
    server = Server()
    player = player_wrapper.make_wrapper()
    downloader = video_downloader.make_video_downloader()
    service_module = ServiceModule(app_facade, player, downloader)
    controller_module = ControllerModule(app_facade, server)

    try:
        server.run(serverConfig.host, serverConfig.port)
    except Exception as e:
        logger.debug("opencast stopped: {}".format(str(e)))


def main(argv=None):
    try:
        _real_main(argv)
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')
