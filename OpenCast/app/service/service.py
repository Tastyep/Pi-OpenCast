""" Abstraction of an applicative service """

import inspect
import traceback
from functools import partial

from OpenCast.infra import Id
from OpenCast.infra.data.repo.error import RepoError
from OpenCast.util.naming import name_handler_method

from .error import OperationError


class Service:
    def __init__(self, app_facade, logger, derived, cmd_module, evt_module=None):
        self._cmd_dispatcher = app_facade.cmd_dispatcher
        self._evt_dispatcher = app_facade.evt_dispatcher
        self._logger = logger
        self.__derived = derived
        self._observe(cmd_module, self._observe_command)
        if evt_module is not None:
            self._observe(evt_module, partial(self._observe_event, None))

    def _observe(self, module, observe_func):
        classes = inspect.getmembers(module, inspect.isclass)
        for _, cls in classes:
            if cls.__module__ == module.__name__:
                observe_func(cls)

    def _observe_command(self, cls):
        self._cmd_dispatcher.observe(cls, self._dispatch_cmd_to_handler)

    def _observe_event(self, cls):
        self._evt_dispatcher.observe({cls: self._dispatch_evt_to_handler})

    def _dispatch_cmd_to_handler(self, cmd):
        handler_name = name_handler_method(cmd.__class__)
        try_count = 1
        while try_count > 0:
            try:
                getattr(self, handler_name)(cmd)
                return
            except RepoError as e:
                # TODO: Reaching outside of the loop should trigger an error
                self._logger.error("Repo error", cmd=cmd, error=e)
                try_count -= 1
            except Exception as e:
                self._logger.error(
                    "Operation error",
                    cmd=cmd,
                    error=e,
                    traceback=traceback.format_exc(),
                )
                self._abort_operation(cmd.id, str(e))
                return

    def _dispatch_evt_to_handler(self, evt):
        handler_name = name_handler_method(evt.__class__)
        try:
            getattr(self, handler_name)(evt)
            return
        except Exception as e:
            self._logger.error(
                "Operation error",
                evt=evt,
                error=e,
                traceback=traceback.format_exc(),
            )
            self._abort_operation(evt.id, str(e))

    def _abort_operation(self, cmd_id: Id, error: str):
        self._evt_dispatcher.dispatch(OperationError(cmd_id, error))

    def _start_transaction(self, repo, cmd_id, impl, *args):
        context = repo.make_context()
        impl(context, *args)
        models = context.entities()
        models_events = []
        for model in models:
            events = model.release_events()
            models_events.append(
                [evtcls(cmd_id, *event[evtcls]) for event in events for evtcls in event]
            )

        context.commit()
        for model_events in models_events:
            for event in model_events:
                self._evt_dispatcher.dispatch(event)
