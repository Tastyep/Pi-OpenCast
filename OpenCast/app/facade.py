from OpenCast.domain.event.dispatcher import EventDispatcher

from .command.dispatcher import CommandDispatcher
from .workflow.factory import WorkflowFactory
from .workflow.manager import WorkflowManager


class AppFacade:
    def __init__(self, app_executor):
        self._cmd_dispatcher = CommandDispatcher(app_executor)
        self._evt_dispatcher = EventDispatcher()
        self._workflow_manager = WorkflowManager(self._evt_dispatcher)
        self._workflow_factory = WorkflowFactory()

    @property
    def cmd_dispatcher(self):
        return self._cmd_dispatcher

    @property
    def evt_dispatcher(self):
        return self._evt_dispatcher

    @property
    def workflow_manager(self):
        return self._workflow_manager

    @property
    def workflow_factory(self):
        return self._workflow_factory
