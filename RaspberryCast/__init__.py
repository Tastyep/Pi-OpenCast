import sys
import os
import yaml
import logging
import logging.config

from .server import run_server


def _real_main(argv):
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    with open('{}/RaspberryCast.yml'.format(app_path), 'r') as data:
        config = yaml.load(data)
    logging.config.dictConfig(config)
    run_server()


def main(argv=None):
    try:
        _real_main(argv)
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')
