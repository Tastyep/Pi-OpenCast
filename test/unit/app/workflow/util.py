import uuid
from test.util import TestCase
from unittest.mock import Mock, PropertyMock

from OpenCast.app.service.error import OperationError
from OpenCast.domain.service.identity import IdentityService
from OpenCast.util.naming import name_factory_method, name_handler_method


class WorkflowTestCase(TestCase):
    def setUp(self):
        self.app_facade = Mock()
        self.factory = Mock()
        self.cmd_dispatcher = Mock()
        self.evt_dispatcher = Mock()
        type(self.app_facade).workflow_factory = PropertyMock(  #
            return_value=self.factory
        )
        type(self.app_facade).cmd_dispatcher = PropertyMock(
            return_value=self.cmd_dispatcher
        )
        type(self.app_facade).evt_dispatcher = PropertyMock(
            return_value=self.evt_dispatcher
        )

    def make_workflow(self, workflow_cls, *args, **kwargs):
        return workflow_cls(uuid.uuid4(), self.app_facade, *args, **kwargs)

    def expect_dispatch(self, cmd_cls, model_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, model_id)
        cmd = cmd_cls(cmd_id, model_id, *args, **kwargs)
        self.cmd_dispatcher.dispatch.assert_called_once_with(cmd)
        return cmd

    def raise_error(self, workflow, cmd):
        self.raise_event(workflow, OperationError, cmd, "")

    def raise_event(self, workflow, evt_cls, *args, **kwargs):
        event = evt_cls(*args, **kwargs)
        getattr(workflow, name_handler_method(evt_cls))(event)

    def expect_workflow_creation(self, wf_cls):
        wf_mock = Mock()
        wf_mock.Completed = wf_cls.Completed
        wf_mock.Aborted = wf_cls.Aborted
        getattr(self.factory, name_factory_method(wf_cls)).return_value = wf_mock
        return wf_mock
