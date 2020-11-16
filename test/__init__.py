import logging
from os import environ

from OpenCast.config import config
from OpenCast.infra.log.module import init as init_logging

# Default the log level to critical for tests.
# Override OPENCAST_LOG_LEVEL to change its value.
config.load_from_dict({"log": {"level": "CRITICAL"}})
config.override_from_env(environ, prefix="OPENCAST")

init_logging("OpenCast")
logging.getLogger("OpenCast").setLevel(config["log.level"])
