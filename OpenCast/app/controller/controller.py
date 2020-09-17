""" Abstraction of an applicative controller """

import inspect

from OpenCast.app.command import make_cmd
from OpenCast.domain.service.identity import IdentityService
from OpenCast.util.naming import name_handler_method, name_factory_method


class Controller:
    def __init__(self, logger, app_facade):
        self._logger = logger
        self._app_facade = app_facade
        self._cmd_dispatcher = app_facade.cmd_dispatcher
        self._evt_dispatcher = app_facade.evt_dispatcher
        self._workflow_manager = app_facade.workflow_manager
        self._workflow_factory = app_facade.workflow_factory

    def _dispatch(self, cmd_cls, component_id, *args, **kwargs):
        cmd = make_cmd(cmd_cls, component_id, *args, **kwargs)
        self._cmd_dispatcher.dispatch(cmd)

    def _observe(self, module, handler_factory):
        classes = inspect.getmembers(module, inspect.isclass)
        for _, cls in classes:
            if cls.__module__ == module.__name__:
                handler = handler_factory(cls)
                self._evt_dispatcher.observe({cls: handler})

    def _default_handler_factory(self, evt_cls):
        handler_name = name_handler_method(evt_cls)
        return getattr(self, handler_name)

    def _start_workflow(self, workflow_cls, resource_id, *args, **kwargs):
        workflow_id = IdentityService.id_workflow(workflow_cls, resource_id)
        workflow = getattr(self._workflow_factory, name_factory_method(workflow_cls))(
            workflow_id, self._app_facade, *args, **kwargs
        )
        return self._workflow_manager.start(workflow)
