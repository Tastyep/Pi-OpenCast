import os

import structlog

from .app.controller.module import ControllerModule
from .app.facade import AppFacade
from .app.service.module import ServiceModule
from .config import config
from .domain.service.factory import ServiceFactory
from .infra.data.facade import DataFacade
from .infra.data.repo.factory import RepoFactory
from .infra.io.facade import IoFacade
from .infra.io.factory import IoFactory
from .infra.log.module import init as init_logging
from .infra.media.facade import MediaFacade
from .infra.media.factory import MediaFactory


def main(argv=None):
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    init_logging(__name__)
    logger = structlog.get_logger(__name__)

    config.load_from_file("{}/config.yml".format(app_path))

    app_facade = AppFacade()

    service_factory = ServiceFactory()

    repo_factory = RepoFactory()
    data_facade = DataFacade(repo_factory)

    io_factory = IoFactory()
    io_facade = IoFacade(io_factory)

    media_factory = MediaFactory(app_facade.evt_dispatcher())
    media_facade = MediaFacade(media_factory)

    ControllerModule(app_facade, data_facade, io_facade, service_factory)
    ServiceModule(app_facade, data_facade, io_facade, media_facade, service_factory)

    try:
        server = io_facade.server()
        server.run(config["server.host"], config["server.port"])
    except Exception as e:
        logger.error(f"{__name__} stopped", error=e)
