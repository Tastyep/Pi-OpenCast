from test.shared.app.facade_mock import AppFacadeMock
from test.shared.infra.facade_mock import InfraFacadeMock
from test.util import TestCase
from unittest.mock import Mock

from OpenCast import run_init_workflow, run_server
from OpenCast.app.workflow.factory import WorkflowFactory
from OpenCast.domain.event.dispatcher import EventDispatcher


class MainTest(TestCase):
    def test_run_server(self):
        logger = Mock()
        infra_facade = InfraFacadeMock()
        self.assertTrue(run_server(logger, infra_facade))

    def test_run_server_with_exception(self):
        logger = Mock()
        infra_facade = InfraFacadeMock()

        def start_server():
            raise Exception("")

        infra_facade.server.start.side_effect = start_server
        self.assertFalse(run_server(logger, infra_facade))
        logger.error.assert_called_once()

    def test_run_init_workflow_success(self):
        app_facade = AppFacadeMock()
        infra_facade = Mock()
        data_facade = Mock()

        app_facade.workflow_factory = WorkflowFactory()
        app_facade.evt_dispatcher = EventDispatcher()

        def start_workflow(workflow):
            workflow.to_COMPLETED()

        app_facade.workflow_manager.start.side_effect = start_workflow
        self.assertTrue(run_init_workflow(app_facade, infra_facade, data_facade))

    def test_run_init_workflow_failure(self):
        app_facade = AppFacadeMock()
        infra_facade = Mock()
        data_facade = Mock()

        app_facade.workflow_factory = WorkflowFactory()
        app_facade.evt_dispatcher = EventDispatcher()

        def start_workflow(workflow):
            workflow.to_ABORTED()

        app_facade.workflow_manager.start.side_effect = start_workflow
        self.assertFalse(run_init_workflow(app_facade, infra_facade, data_facade))
