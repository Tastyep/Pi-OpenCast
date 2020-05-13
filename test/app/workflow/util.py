import re
import uuid
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.app.service.error import OperationError
from OpenCast.domain.service.identity import IdentityService


class WorkflowTestCase(TestCase):
    def setUp(self):
        self.cmd_dispatcher = Mock()
        self.evt_dispatcher = Mock()
        self.workflow_id = uuid.uuid4()

    def expect_dispatch(self, cmd_cls, model_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, model_id)
        cmd = cmd_cls(cmd_id, model_id, *args, **kwargs)
        self.cmd_dispatcher.dispatch.assert_called_once_with(cmd)
        return cmd

    def raise_error(self, workflow, cmd):
        self.raise_event(workflow, OperationError, cmd, "")

    def raise_event(self, workflow, evt_cls, *args, **kwargs):
        handler_name = re.sub("([A-Z]+)", r"_\1", evt_cls.__name__).lower()
        event = evt_cls(*args, **kwargs)
        getattr(workflow, handler_name)(event)
