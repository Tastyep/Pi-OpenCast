import logging
import logging.config
import os
import sys

import yaml

from .app.controller.module import ControllerModule
from .app.facade import AppFacade
from .app.service.module import ServiceModule
from .config import config
from .domain.service.factory import ServiceFactory
from .infra.data.facade import DataFacade
from .infra.data.repo.factory import RepoFactory
from .infra.io.facade import IoFacade
from .infra.io.factory import IoFactory
from .infra.media.facade import MediaFacade
from .infra.media.factory import MediaFactory


def _real_main():
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    with open("{}/logging.yml".format(app_path), "r") as file:
        cfg = yaml.load(file, Loader=yaml.Loader)
        logging.config.dictConfig(cfg)
    logger = logging.getLogger(__name__)

    config.load_from_file("{}/config.ini".format(app_path))
    server_config = config["Server"]

    app_facade = AppFacade()

    service_factory = ServiceFactory()

    repo_factory = RepoFactory()
    data_facade = DataFacade(repo_factory)

    io_factory = IoFactory()
    io_facade = IoFacade(io_factory)

    media_factory = MediaFactory(app_facade.evt_dispatcher())
    media_facade = MediaFacade(media_factory)

    controller_module = ControllerModule(app_facade, data_facade, io_facade)
    service_module = ServiceModule(
        app_facade, data_facade, io_facade, media_facade, service_factory
    )

    try:
        server = io_facade.server()
        server.run(server_config.host, server_config.port)
    except Exception as e:
        logger.debug(f"opencast stopped: {e}")


def main(argv=None):
    try:
        _real_main()
    except KeyboardInterrupt:
        sys.exit("\nERROR: Interrupted by user")
