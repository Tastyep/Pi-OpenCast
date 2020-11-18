""" Manager and coordinator of workflows """

from threading import RLock

import structlog

from . import Id


class WorkflowManager:
    def __init__(self, evt_dispatcher):
        self._logger = structlog.get_logger(__name__)
        self._evt_dispatcher = evt_dispatcher
        self._workflow_ids = []
        self._lock = RLock()

    def is_running(self, workflow_id: Id):
        with self._lock:
            return workflow_id in self._workflow_ids

    def start(self, workflow, *args, **kwargs):
        def on_completion(_):
            with self._lock:
                self._logger.debug("Removing workflow", workflow=workflow)
                self._workflow_ids.remove(workflow.id)

        with self._lock:
            if self.is_running(workflow.id):
                self._logger.info("workflow already active", workflow=workflow)
                return False

            self._workflow_ids.append(workflow.id)
            self._evt_dispatcher.observe_result(
                workflow.id,
                {workflow.Completed: on_completion, workflow.Aborted: on_completion},
                times=1,
            )

        self._logger.info("Starting workflow", workflow=workflow)
        workflow.start(*args, **kwargs)
        return True
