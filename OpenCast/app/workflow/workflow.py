import re

import structlog
from transitions import Machine


class Workflow(Machine):
    def __init__(self, derived, id, cmd_dispatcher, evt_dispatcher, *args, **kwargs):
        super(Workflow, self).__init__(
            model=self,
            states=derived.States,
            transitions=derived.transitions,
            *args,
            **kwargs,
        )
        self._logger = structlog.get_logger(__name__)

        self.id = id
        self._cmd_dispatcher = cmd_dispatcher
        self._evt_dispatcher = evt_dispatcher
        self.__derived = derived
        self._sub_workflows = []

    def reset(self):
        self.set_state(self._initial)
        for workflow in self._sub_workflows:
            workflow.reset()

    def cancel(self, *args):
        self._evt_dispatcher.dispatch(self.__derived.Aborted(self.id, *args))

    def _complete(self, *args):
        self._evt_dispatcher.dispatch(self.__derived.Completed(self.id, *args))

    def _abort(self, *args):
        self._evt_dispatcher.dispatch(self.__derived.Aborted(self.id, *args))

    def _child_workflow(self, cls, *args, **kwargs):
        workflow = cls(
            self.id, self._cmd_dispatcher, self._evt_dispatcher, *args, **kwargs,
        )
        self._sub_workflows.append(workflow)
        return workflow

    def _observe_start(self, workflow, *args, **kwargs):
        self._observe(workflow.Completed)
        self._observe(workflow.Aborted)
        workflow.start(*args, **kwargs)

    def _observe(self, evt):
        handler = self._event_handler(evt)
        self._evt_dispatcher.observe_id(evt, self.id, handler, times=1)

    def _observe_dispatch(self, evt, cmd, *args, **kwargs):
        self._observe(evt)
        self._cmd_dispatcher.dispatch(cmd(self.id, *args, **kwargs))

    def _event_handler(self, evt):
        handler_name = re.sub("([A-Z]+)", r"_\1", evt.__name__).lower()
        try:
            return getattr(self.__derived, handler_name)
        except AttributeError:
            self._logger.error(
                "Missing handler", handler=handler_name, cls=evt.__name__
            )
            # Raise the exception as it is a developer error
            raise
