import asyncio
import json
from test.integration.app.event_expecter import EventExpecter
from test.shared.infra.data.producer import DataProducer
from test.shared.infra.facade_mock import InfraFacadeMock
from unittest.mock import Mock

import aiohttp
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp.web import Application

from OpenCast.app.controller.module import ControllerModule
from OpenCast.app.facade import AppFacade
from OpenCast.app.service.module import ServiceModule
from OpenCast.app.tool.json_encoder import EventEncoder
from OpenCast.domain.service.factory import ServiceFactory
from OpenCast.infra.data.manager import DataManager, StorageType
from OpenCast.infra.data.repo.factory import RepoFactory
from OpenCast.infra.io.factory import IoFactory
from OpenCast.infra.io.server import Server


class MonitorControllerTestCase(AioHTTPTestCase):
    WS_EVENT_TIMEOUT = 1.0

    def setUp(self):
        def execute_handler(handler, *args):
            handler(*args)

        app_executor = Mock()
        app_executor.submit = Mock(side_effect=execute_handler)
        self.app_facade = AppFacade(app_executor)
        self.evt_dispatcher = self.app_facade.evt_dispatcher

        repo_factory = RepoFactory()
        data_manager = DataManager(repo_factory)
        self.data_facade = data_manager.connect(StorageType.MEMORY)
        self.data_producer = DataProducer.make()
        self.data_producer.player().populate(self.data_facade)

        infraServiceFactory = Mock()
        self.service_factory = ServiceFactory(infraServiceFactory)

        self.downloader = Mock()
        self.video_parser = Mock()
        self.infra_facade = InfraFacadeMock()
        self.infra_facade.media_factory.make_downloader.return_value = self.downloader
        self.infra_facade.media_factory.make_video_parser.return_value = (
            self.video_parser
        )

        self.app = Application()
        server = Server(self.app)
        self.infra_facade.server = server
        self.infra_facade.io_factory = IoFactory()

        self.evt_expecter = EventExpecter(
            self.app_facade.cmd_dispatcher, self.app_facade.evt_dispatcher
        )

        ControllerModule(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )
        ServiceModule(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )

        super(MonitorControllerTestCase, self).setUp()

    async def expect_ws_events(self, ws, events):
        for event in events:
            msg = await asyncio.wait_for(ws.receive(), self.WS_EVENT_TIMEOUT)
            self.assertEqual(aiohttp.WSMsgType.TEXT, msg.type)
            self.assertEqual(
                json.dumps(
                    {"name": type(event).__name__, "event": event}, cls=EventEncoder
                ),
                msg.data,
            )

    async def get_application(self) -> Application:
        return self.app
