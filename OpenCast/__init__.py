import logging
import os
from concurrent.futures import ThreadPoolExecutor

import structlog
from vlc import Instance as VlcInstance

from .app.controller.module import ControllerModule
from .app.facade import AppFacade
from .app.service.module import ServiceModule
from .config import ConfigError, config
from .domain.model.player import Player
from .domain.service.factory import ServiceFactory
from .domain.service.identity import IdentityService
from .infra.data.facade import DataFacade
from .infra.data.repo.factory import RepoFactory
from .infra.facade import InfraFacade
from .infra.io.factory import IoFactory
from .infra.log.module import init as init_logging
from .infra.media.factory import MediaFactory
from .infra.service.factory import ServiceFactory as InfraServiceFactory


def main(argv=None):
    app_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    init_logging(__name__)

    try:
        config.load_from_file("{}/config.yml".format(app_path))
    except ConfigError:
        return

    # Get and update the log level
    logging.getLogger(__name__).setLevel(config["log.level"])
    logger = structlog.get_logger(__name__)

    # TODO: make worker count configurable
    app_executor = ThreadPoolExecutor(max_workers=1)
    app_facade = AppFacade(app_executor)

    infra_service_factory = InfraServiceFactory()
    service_factory = ServiceFactory(infra_service_factory)

    repo_factory = RepoFactory()
    data_facade = DataFacade(repo_factory)
    data_facade.player_repo.create(Player(IdentityService.id_player()))

    io_factory = IoFactory()
    media_factory = MediaFactory(
        VlcInstance(), ThreadPoolExecutor(config["downloader.max_concurrency"])
    )
    infra_facade = InfraFacade(io_factory, media_factory)

    ControllerModule(app_facade, infra_facade, data_facade, service_factory)
    ServiceModule(app_facade, infra_facade, data_facade, service_factory)

    try:
        server = infra_facade.server
        server.run(config["server.host"], config["server.port"])
    except Exception as e:
        logger.error(f"{__name__} stopped", error=e)
