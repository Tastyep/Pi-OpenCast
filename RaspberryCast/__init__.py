import sys
import os
import yaml
import logging
import logging.config
from .server import Server
from .config import config


def _real_main(argv):
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    with open('{}/logging.yml'.format(app_path), 'r') as file:
        cfg = yaml.load(file)
        logging.config.dictConfig(cfg)

    config.load('{}/config.ini'.format(app_path))

    s = Server()
    s.run()


def main(argv=None):
    try:
        _real_main(argv)
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')
