from OpenCast.domain.event.dispatcher import EventDispatcher

from .command.dispatcher import CommandDispatcher
from .workflow.factory import WorkflowFactory


class AppFacade:
    def __init__(self, app_executor):
        self._cmd_dispatcher = CommandDispatcher(app_executor)
        self._evt_dispatcher = EventDispatcher()
        self._workflow_factory = WorkflowFactory()

    @property
    def cmd_dispatcher(self):
        return self._cmd_dispatcher

    @property
    def evt_dispatcher(self):
        return self._evt_dispatcher

    @property
    def workflow_factory(self):
        return self._workflow_factory
