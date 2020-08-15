from OpenCast.app.command import make_cmd
from OpenCast.app.service.error import OperationError
from OpenCast.util.naming import name_handler_method
from transitions import Machine

from . import Id


class Workflow(Machine):
    def __init__(
        self, logger, derived, id_: Id, app_facade, *args, **kwargs,
    ):
        super().__init__(
            model=self,
            states=derived.States,
            transitions=derived.transitions,
            *args,
            **kwargs,
        )
        self._logger = logger

        self.id = id_
        self._app_facade = app_facade
        self._factory = app_facade.workflow_factory
        self._cmd_dispatcher = app_facade.cmd_dispatcher
        self._evt_dispatcher = app_facade.evt_dispatcher
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

    def _observe_start(self, workflow, *args, **kwargs):
        self._observe(workflow.id, [workflow.Completed, workflow.Aborted])
        if self._app_facade.workflow_manager.start(workflow, *args, **kwargs):
            self._sub_workflows.append(workflow)

    def _observe_dispatch(self, evt_cls, cmd_cls, model_id: Id, *args, **kwargs):
        cmd = make_cmd(cmd_cls, model_id, *args, **kwargs)
        self._observe(cmd.id, [evt_cls, OperationError])
        self._cmd_dispatcher.dispatch(cmd)

    def _observe(self, cmd_id: Id, evt_clss: list):
        evtcls_to_handler = {
            evt_cls: self._event_handler(evt_cls) for evt_cls in evt_clss
        }
        self._evt_dispatcher.observe(cmd_id, evtcls_to_handler, times=1)

    def _event_handler(self, evt_cls):
        handler_name = name_handler_method(evt_cls)
        try:
            return getattr(self.__derived, handler_name)
        except AttributeError:
            self._logger.error(
                "Missing handler", handler=handler_name, cls=evt_cls.__name__
            )
            # Raise the exception as it is a developer error
            raise
