from test.util import TestCase
from unittest.mock import Mock

from OpenCast.app.workflow import Id
from OpenCast.app.workflow.manager import WorkflowManager
from OpenCast.app.workflow.player import QueueVideoWorkflow
from OpenCast.domain.service.identity import IdentityService


class WorkflowManagerTest(TestCase):
    def setUp(self):
        self.evt_dispatcher = Mock()
        self.manager = WorkflowManager(self.evt_dispatcher)

        video_id = IdentityService.id_video("source")
        self.workflow = Mock()
        self.queue_workflow_id = IdentityService.id_workflow(
            QueueVideoWorkflow, video_id
        )

    def test_is_running_none(self):
        self.assertFalse(self.manager.is_running(self.queue_workflow_id))

    def test_start(self):
        self.workflow.id = self.queue_workflow_id
        self.workflow.complete = None

        def fake_observe(workflow_id: Id, evtcls_handler: dict, times: int):
            self.assertEqual(1, times)
            self.assertEqual(self.workflow.id, workflow_id)
            self.assertTrue(evtcls_handler)
            self.workflow.complete = evtcls_handler.get(self.workflow.Completed, None)

        self.evt_dispatcher.observe_result.side_effect = fake_observe

        self.assertTrue(self.manager.start(self.workflow))
        self.assertTrue(self.manager.is_running(self.workflow.id))

        self.assertNotEqual(None, self.workflow.complete)
        self.workflow.complete(None)

        self.assertFalse(self.manager.is_running(self.workflow.id))

    def test_start_duplicate(self):
        self.workflow.id = self.queue_workflow_id
        self.workflow.complete = None

        def fake_observe(workflow_id: Id, evtcls_handler: dict, times: int):
            self.workflow.complete = evtcls_handler.get(self.workflow.Completed, None)

        self.evt_dispatcher.observe_result.side_effect = fake_observe

        self.assertTrue(self.manager.start(self.workflow))
        self.assertFalse(self.manager.start(self.workflow))
        self.assertTrue(self.manager.is_running(self.workflow.id))

        self.workflow.complete(None)
        self.assertFalse(self.manager.is_running(self.workflow.id))

        self.assertTrue(self.manager.start(self.workflow))
