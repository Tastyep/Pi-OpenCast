import asyncio
import json
from test.integration.app.event_expecter import EventExpecter
from test.shared.app.facade_mock import AppFacadeMock
from test.shared.infra.data.producer import DataProducer
from test.shared.infra.facade_mock import InfraFacadeMock
from unittest.mock import Mock

import aiohttp
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp.web import Application

from OpenCast.app.controller.module import ControllerModule
from OpenCast.app.service.error import OperationError
from OpenCast.app.service.module import ServiceModule
from OpenCast.app.tool.json_encoder import EventEncoder
from OpenCast.domain.event.dispatcher import EventDispatcher
from OpenCast.infra.data.manager import DataManager, StorageType
from OpenCast.infra.data.repo.factory import RepoFactory
from OpenCast.infra.io.factory import IoFactory
from OpenCast.infra.io.server import make_server


class MonitorControllerTestCase(AioHTTPTestCase):
    WS_EVENT_TIMEOUT = 1.0

    def setUp(self):
        self.app_facade = AppFacadeMock()
        self.evt_dispatcher = EventDispatcher()
        self.app_facade.evt_dispatcher = self.evt_dispatcher

        repo_factory = RepoFactory()
        data_manager = DataManager(repo_factory)
        self.data_facade = data_manager.connect(StorageType.MEMORY)
        self.data_producer = DataProducer.make()
        self.data_producer.player().populate(self.data_facade)

        self.service_factory = Mock()
        self.source_service = Mock()
        self.queueing_service = Mock()
        self.service_factory.make_source_service.return_value = self.source_service
        self.service_factory.make_queueing_service.return_value = self.queueing_service

        self.downloader = Mock()
        self.video_parser = Mock()
        self.infra_facade = InfraFacadeMock()
        self.infra_facade.media_factory.make_downloader.return_value = self.downloader
        self.infra_facade.media_factory.make_video_parser.return_value = (
            self.video_parser
        )

        server = make_server()
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

    def hook_cmd(self, cmd_cls, callback):
        def impl(command):
            if type(command) is cmd_cls:
                callback(command)

        self.app_facade.cmd_dispatcher.dispatch.side_effect = impl

    def error_on(self, cmd_cls, *args, **kwargs):
        def raise_error(command):
            self.app_facade.evt_dispatcher.dispatch(
                OperationError(command.id, *args, **kwargs)
            )

        self.hook_cmd(cmd_cls, raise_error)

    def expect_and_raise(self, cmd, events):
        def respond_to_cmd(command):
            self.assertEqual(command, cmd)
            for evt in events:
                self.app_facade.evt_dispatcher.dispatch(
                    evt["type"](cmd.id, cmd.model_id, **evt["args"])
                )

        self.app_facade.cmd_dispatcher.dispatch.side_effect = respond_to_cmd

    def expect_and_raise_l(self, datas: list):
        iterator = iter(datas)

        def respond_to_cmd(command):
            data = next(iterator)
            cmd = data["cmd"]
            self.assertEqual(command, cmd)
            if data.get("hook", None) is not None:
                data["hook"](cmd)
            evt = data["evt"]
            if evt is OperationError:
                self.app_facade.evt_dispatcher.dispatch(evt(cmd.id, **data["args"]))
            else:
                self.app_facade.evt_dispatcher.dispatch(
                    evt(cmd.id, cmd.model_id, **data["args"])
                )

        self.app_facade.cmd_dispatcher.dispatch.side_effect = respond_to_cmd

    def expect_and_error(self, cmd, error=""):
        def error_to_cmd(command):
            self.assertEqual(command, cmd)
            self.app_facade.evt_dispatcher.dispatch(OperationError(cmd.id, error))

        self.app_facade.cmd_dispatcher.dispatch.side_effect = error_to_cmd

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
        return self.infra_facade.server.app
