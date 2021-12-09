""" OpenCast application's backend """

import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from queue import SimpleQueue

import structlog
from vlc import Instance as VlcInstance

from .app.controller.module import ControllerModule
from .app.facade import AppFacade
from .app.service.module import ServiceModule
from .app.tool.json_encoder import ModelEncoder
from .config import settings
from .domain.service.factory import ServiceFactory
from .domain.service.identity import IdentityService
from .infra.data.cache import TimeBasedCache
from .infra.data.manager import DataManager, StorageType
from .infra.data.repo.factory import RepoFactory
from .infra.facade import InfraFacade
from .infra.io.factory import IoFactory
from .infra.log.module import init as init_logging
from .infra.media.factory import MediaFactory
from .infra.service.factory import ServiceFactory as InfraServiceFactory


def run_server(logger, infra_facade):
    try:
        infra_facade.server.start(
            settings["server.host"],
            settings["server.port"],
            settings["log.api_trafic"],
        )
    except Exception as e:
        logger.error(
            "Server exception caught", error=e, traceback=traceback.format_exc()
        )
        return False
    return True


def run_init_workflow(app_facade, data_facade):
    queue = SimpleQueue()

    workflow_id = IdentityService.random()
    workflow = app_facade.workflow_factory.make_init_workflow(
        workflow_id, app_facade, data_facade
    )
    app_facade.evt_dispatcher.observe(
        {workflow.Completed: queue.put, workflow.Aborted: queue.put}, times=1
    )
    app_facade.workflow_manager.start(workflow)

    queue.get()
    return workflow.is_COMPLETED()


def main(argv=None):
    logger = structlog.get_logger(__name__)

    try:
        settings.validators.validate()
    except Exception as error:
        logger.error("configuration error", error=str(error))
        return

    init_logging(__name__)

    # TODO: make worker count configurable
    app_executor = ThreadPoolExecutor(max_workers=1)
    app_facade = AppFacade(app_executor)

    infra_service_factory = InfraServiceFactory()
    service_factory = ServiceFactory(infra_service_factory)

    repo_factory = RepoFactory()
    data_manager = DataManager(repo_factory)
    data_facade = data_manager.connect(
        StorageType.JSON,
        path=settings["database.file"],
        indent=4,
        separators=(",", ": "),
        cls=ModelEncoder,
    )

    io_factory = IoFactory()
    downloader_executor = ThreadPoolExecutor(settings["downloader.max_concurrency"])
    media_cache = TimeBasedCache(max_duration=timedelta(minutes=2))
    media_factory = MediaFactory(VlcInstance(), downloader_executor, media_cache)
    infra_facade = InfraFacade(io_factory, media_factory, infra_service_factory)

    ControllerModule(app_facade, infra_facade, data_facade, service_factory)
    ServiceModule(app_facade, infra_facade, data_facade, service_factory)

    if run_init_workflow(app_facade, data_facade):
        run_server(logger, infra_facade)
