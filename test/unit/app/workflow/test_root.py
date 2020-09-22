from pathlib import Path
from test.shared.infra.data.facade_mock import DataFacadeMock
from test.shared.infra.facade_mock import InfraFacadeMock
from unittest.mock import Mock

from OpenCast.app.workflow.root import RootWorkflow
from OpenCast.app.workflow.video import VideoWorkflow

from .util import WorkflowTestCase


class RootWorkflowTest(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.video_repo = Mock()
        self.infra_facade = InfraFacadeMock()
        self.data_facade = DataFacadeMock()

        self.file_service = Mock()
        self.infra_facade.service_factory.make_file_service.return_value = (
            self.file_service
        )

        self.workflow = self.make_workflow(
            RootWorkflow, self.infra_facade, self.data_facade
        )

    def test_initial(self):
        self.assertTrue(self.workflow.is_INITIAL())

    def test_init_to_loading(self):
        self.file_service.list_directory.return_value = []
        self.workflow.start()

    def test_loading_to_running(self):
        local_files = [
            Mock(),
            Mock(),
        ]
        self.file_service.list_directory.return_value = local_files
        for file in local_files:
            file.is_file.return_value = True

        wf_mocks = self.expect_workflow_creation(VideoWorkflow, 2)

        self.workflow.to_LOADING()

        for mock in wf_mocks:
            mock.start.assert_called_once()
        self.assertTrue(self.workflow.is_RUNNING())

    def test_running_to_aborted(self):
        def raise_exception(*_):
            raise RuntimeError("server stopped")

        self.infra_facade.server.start.side_effect = raise_exception
        self.workflow.to_RUNNING()
        self.assertTrue(self.workflow.is_ABORTED())
