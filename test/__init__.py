import os
import yaml
import logging
import logging.config

if "OPENCAST_ENABLE_LOGGING" in os.environ:
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    with open('{}/logging.yml'.format(app_path), 'r') as file:
        cfg = yaml.load(file)
        logging.config.dictConfig(cfg)
