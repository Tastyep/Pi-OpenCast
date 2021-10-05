""" Workflow abstraction using finite-state machines """

from transitions import Machine

from OpenCast.app.command import make_cmd
from OpenCast.app.service.error import OperationError
from OpenCast.util.naming import name_handler_method

from . import Id


class Workflow(Machine):
    """Workflow base class

    Args:
        logger: The workflow's logger.
        id: The workflow's ID.
        app_facade: The application facade.

    Attributes:
        id: The workflow's ID.
    """

    def __init__(
        self,
        logger,
        id_: Id,
        app_facade,
        *args,
        **kwargs,
    ):
        super().__init__(
            model=self,
            states=self.States,
            transitions=self.transitions,
            *args,
            **kwargs,
        )
        self._logger = logger

        self.id = id_
        self._app_facade = app_facade
        self._factory = app_facade.workflow_factory
        self._cmd_dispatcher = app_facade.cmd_dispatcher
        self._evt_dispatcher = app_facade.evt_dispatcher

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id})"

    def _cancel(self, *args):
        """Cancel the workflow and dispatch the related event"""
        self._evt_dispatcher.dispatch(self.Aborted(self.id, *args))

    def _complete(self, *args):
        self._evt_dispatcher.dispatch(self.Completed(self.id, *args))

    def _observe_start(self, workflow, *args, **kwargs):
        self._observe(workflow.id, [workflow.Completed, workflow.Aborted])
        self._start_workflow(workflow, *args, **kwargs)

    def _start_workflow(self, workflow, *args, **kwargs):
        self._app_facade.workflow_manager.start(workflow, *args, **kwargs)

    def _observe_dispatch(self, evt_cls, cmd_cls, model_id: Id, *args, **kwargs):
        cmd = make_cmd(cmd_cls, model_id, *args, **kwargs)
        self._observe(cmd.id, [evt_cls, OperationError])
        self._cmd_dispatcher.dispatch(cmd)

    def _observe(self, cmd_id: Id, evt_clss: list):
        evtcls_to_handler = {
            evt_cls: self._event_handler(evt_cls) for evt_cls in evt_clss
        }
        self._evt_dispatcher.observe_result(cmd_id, evtcls_to_handler, times=1)

    def _observe_group(self, cmd_ids_to_evt_clss: dict[Id, list]):
        cmd_ids_to_evt_cls_to_handler = {
            cmd_id: {evt_cls: self._event_handler(evt_cls) for evt_cls in evt_clss}
            for cmd_id, evt_clss in cmd_ids_to_evt_clss.items()
        }
        self._evt_dispatcher.observe_group(cmd_ids_to_evt_cls_to_handler, times=1)

    def _event_handler(self, evt_cls):
        handler_name = name_handler_method(evt_cls)
        try:
            return getattr(self, handler_name)
        except AttributeError:
            self._logger.critical(
                "Missing handler", handler=handler_name, cls=evt_cls.__name__
            )
            # Raise the exception as it is a developer error
            raise
