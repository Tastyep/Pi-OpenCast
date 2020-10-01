from test.shared.app.facade_mock import AppFacadeMock
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.app.service.error import OperationError
from OpenCast.domain.event.dispatcher import EventDispatcher
from OpenCast.domain.service.identity import IdentityService
from OpenCast.util.naming import name_factory_method


class WorkflowTestCase(TestCase):
    def setUp(self):
        self.app_facade = AppFacadeMock()

        def start_workflow(workflow):
            workflow.start()
            return True

        self.app_facade.workflow_manager.start.side_effect = start_workflow
        self.app_facade.evt_dispatcher = EventDispatcher()

    def make_workflow(self, workflow_cls, *args, **kwargs):
        return workflow_cls(IdentityService.random(), self.app_facade, *args, **kwargs)

    def expect_dispatch(self, cmd_cls, model_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, model_id)
        cmd = cmd_cls(cmd_id, model_id, *args, **kwargs)
        self.app_facade.cmd_dispatcher.dispatch.assert_called_once_with(cmd)
        self.app_facade.cmd_dispatcher.dispatch.reset_mock()
        return cmd

    def raise_error(self, cmd):
        self.raise_event(OperationError, cmd.id, "")

    def raise_event(self, evt_cls, *args, **kwargs):
        event = evt_cls(*args, **kwargs)
        self.app_facade.evt_dispatcher.dispatch(event)

    def expect_workflow_creation(self, wf_cls, times=1):
        mocks = []
        for i in range(times):
            wf_mock = Mock()
            wf_mock.Completed = wf_cls.Completed
            wf_mock.Aborted = wf_cls.Aborted
            mocks.append(wf_mock)

        getattr(
            self.app_facade.workflow_factory, name_factory_method(wf_cls)
        ).side_effect = mocks

        return tuple(mocks)
