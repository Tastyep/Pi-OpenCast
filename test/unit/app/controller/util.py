from test.shared.app.facade_mock import AppFacadeMock
from test.shared.infra.data.producer import DataProducer
from test.util import TestCase

from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.manager import DataManager, StorageType
from OpenCast.infra.data.repo.factory import RepoFactory
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
