import asyncio
from test.shared.app.facade_mock import AppFacadeMock
from test.shared.infra.data.producer import DataProducer
from test.shared.infra.facade_mock import InfraFacadeMock
from test.util import TestCase
from unittest import IsolatedAsyncioTestCase

from aiohttp.test_utils import make_mocked_request

from OpenCast.app.service.error import OperationError
from OpenCast.domain.event.dispatcher import EventDispatcher
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.manager import DataManager, StorageType
from OpenCast.infra.data.repo.factory import RepoFactory
from OpenCast.infra.io.factory import IoFactory
from OpenCast.util.naming import name_handler_method


class ControllerTestCase(TestCase):
    def setUp(self):
        self.app_facade = AppFacadeMock()

        repo_factory = RepoFactory()
        data_manager = DataManager(repo_factory)
        self.data_facade = data_manager.connect(StorageType.MEMORY)

        self.data_producer = DataProducer.make()

    def expect_dispatch(self, cmd_cls, model_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, model_id)
        cmd = cmd_cls(cmd_id, model_id, *args, **kwargs)
        self.app_facade.cmd_dispatcher.dispatch.assert_called_once_with(cmd)
        return cmd

    def raise_event(self, controller, evt_cls, *args, **kwargs):
        event = evt_cls(*args, **kwargs)
        getattr(controller, name_handler_method(evt_cls))(event)


class MonitorControllerTestCase(IsolatedAsyncioTestCase):
    REQ_HANDLER_TIMEOUT = 1

    def setUp(self):
        self.app_facade = AppFacadeMock()
        self.app_facade.evt_dispatcher = EventDispatcher()

        repo_factory = RepoFactory()
        data_manager = DataManager(repo_factory)
        self.data_facade = data_manager.connect(StorageType.MEMORY)
        self.data_producer = DataProducer.make()

        self.infra_facade = InfraFacadeMock()
        self.infra_facade.io_factory = IoFactory()
        self.infra_facade.server.make_json_response.side_effect = (
            lambda status, body, _: (
                status,
                body,
            )
        )

    def make_request(
        self, method: str, url: str, match_info: dict = {}, query: dict = None
    ):
        if query is not None:
            first = True
            for k, v in query.items():
                if first:
                    url = f"{url}?{k}={v}"
                    first = False
                else:
                    url = f"{url}&{k}={v}"

        return make_mocked_request(method, url, match_info=match_info)

    def hook_cmd(self, cmd_cls, callback):
        def impl(command):
            if type(command) is cmd_cls:
                callback(command)

        self.app_facade.cmd_dispatcher.dispatch.side_effect = impl

    def check_and_raise(self, cmd, evt_cls, *args, **kwargs):
        def respond_to_cmd(command):
            self.assertEqual(command, cmd)
            self.app_facade.evt_dispatcher.dispatch(
                evt_cls(cmd.id, cmd.model_id, *args, **kwargs)
            )

        self.app_facade.cmd_dispatcher.dispatch.side_effect = respond_to_cmd

    def check_and_raise_l(self, datas: list):
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

    def check_and_error(self, cmd, error=""):
        def error_to_cmd(command):
            self.assertEqual(command, cmd)
            self.app_facade.evt_dispatcher.dispatch(OperationError(cmd.id, error))

        self.app_facade.cmd_dispatcher.dispatch.side_effect = error_to_cmd

    def error_on(self, cmd_cls, *args, **kwargs):
        def raise_error(command):
            self.app_facade.evt_dispatcher.dispatch(
                OperationError(command.id, *args, **kwargs)
            )

        self.hook_cmd(cmd_cls, raise_error)

    async def route(self, coro, *args):
        return await asyncio.wait_for(coro(*args), timeout=self.REQ_HANDLER_TIMEOUT)
