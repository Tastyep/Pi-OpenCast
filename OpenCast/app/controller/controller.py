import inspect

from OpenCast.domain.service.identity import IdentityService
from OpenCast.util.naming import name_handler_method


class Controller:
    def __init__(self, app_facade):
        self._app_facade = app_facade
        self._cmd_dispatcher = app_facade.cmd_dispatcher
        self._evt_dispatcher = app_facade.evt_dispatcher

    def _dispatch(self, cmd_cls, component_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, component_id)
        self._cmd_dispatcher.dispatch(cmd_cls(cmd_id, component_id, *args, **kwargs))

    def _observe(self, module):
        classes = inspect.getmembers(module, inspect.isclass)
        for _, cls in classes:
            if cls.__module__ == module.__name__:
                handler_name = name_handler_method(cls)
                self._evt_dispatcher.observe(None, {cls: getattr(self, handler_name)})

    def _start_workflow(self, workflow_cls, resource_id, *args, **kwargs):
        workflow_id = IdentityService.id_workflow(workflow_cls, resource_id)
        workflow = workflow_cls(workflow_id, self._app_facade, *args, **kwargs)
        workflow.start()
        return workflow
