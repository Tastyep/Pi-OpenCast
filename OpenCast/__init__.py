""" OpenCast application's backend """

import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from queue import SimpleQueue

import structlog
from vlc import Instance as VlcInstance

from .app.controller.module import ControllerModule
from .app.facade import AppFacade
from .app.service.module import ServiceModule
from .app.tool.json_encoder import ModelEncoder
from .config import ConfigError, config
from .domain.service.factory import ServiceFactory
from .domain.service.identity import IdentityService
from .infra.data.manager import DataManager, StorageType
from .infra.data.repo.factory import RepoFactory
from .infra.facade import InfraFacade
from .infra.io.factory import IoFactory
from .infra.log.module import init as init_logging
from .infra.media.factory import MediaFactory
from .infra.service.factory import ServiceFactory as InfraServiceFactory


def run_server(logger, infra_facade):
    try:
        infra_facade.server.start(config["server.host"], config["server.port"])
    except Exception as e:
        logger.error(
            "Server exception caught", error=e, traceback=traceback.format_exc()
        )
        return False
    return True


def run_init_workflow(app_facade, infra_facade, data_facade):
    queue = SimpleQueue()

    workflow_id = IdentityService.random()
    workflow = app_facade.workflow_factory.make_init_workflow(
        workflow_id, app_facade, infra_facade, data_facade
    )
    app_facade.evt_dispatcher.observe(
        {workflow.Completed: queue.put, workflow.Aborted: queue.put}, times=1
    )
    app_facade.workflow_manager.start(workflow)

    queue.get()
    return workflow.is_COMPLETED()


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
    data_manager = DataManager(repo_factory)
    data_facade = data_manager.connect(
        StorageType.JSON,
        path=config["database.file"],
        indent=4,
        separators=(",", ": "),
        cls=ModelEncoder,
    )

    io_factory = IoFactory()
    media_factory = MediaFactory(
        VlcInstance(), ThreadPoolExecutor(config["downloader.max_concurrency"])
    )
    infra_facade = InfraFacade(io_factory, media_factory, infra_service_factory)

    ControllerModule(app_facade, infra_facade, data_facade, service_factory)
    ServiceModule(app_facade, infra_facade, data_facade, service_factory)

    if run_init_workflow(app_facade, infra_facade, data_facade):
        run_server(logger, infra_facade)
