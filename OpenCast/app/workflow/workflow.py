import re

from OpenCast.app.service.error import OperationError
from OpenCast.domain.service.identity import IdentityService
from transitions import Machine


class Workflow(Machine):
    def __init__(
        self, logger, derived, id, cmd_dispatcher, evt_dispatcher, *args, **kwargs
    ):
        super(Workflow, self).__init__(
            model=self,
            states=derived.States,
            transitions=derived.transitions,
            *args,
            **kwargs,
        )
        self._logger = logger

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
        self._observe(self.id, [workflow.Completed, workflow.Aborted])
        workflow.start(*args, **kwargs)

    def _observe_dispatch(self, evt_cls, cmd_cls, model_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, model_id)
        self._observe(cmd_id, [evt_cls, OperationError])
        self._cmd_dispatcher.dispatch(cmd_cls(cmd_id, model_id, *args, **kwargs))

    def _observe(self, cmd_id, evt_clss: list):
        evtcls_to_handler = {
            evt_cls: self._event_handler(evt_cls) for evt_cls in evt_clss
        }
        self._evt_dispatcher.observe(cmd_id, evtcls_to_handler, times=1)

    def _event_handler(self, evt_cls):
        handler_name = re.sub("([A-Z]+)", r"_\1", evt_cls.__name__).lower()
        try:
            return getattr(self.__derived, handler_name)
        except AttributeError:
            self._logger.error(
                "Missing handler", handler=handler_name, cls=evt_cls.__name__
            )
            # Raise the exception as it is a developer error
            raise
