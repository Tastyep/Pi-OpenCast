import inspect
import re
from functools import partial

from OpenCast.infra.data.repo.error import RepoError

from .error import OperationError


class Service:
    def __init__(self, app_facade, logger, derived, cmd_module, evt_module=None):
        self._cmd_dispatcher = app_facade.cmd_dispatcher()
        self._evt_dispatcher = app_facade.evt_dispatcher()
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
        self._cmd_dispatcher.observe(cls, self._dispatch_to_handler)

    def _observe_event(self, evt_id, cls):
        self._evt_dispatcher.observe(evt_id, {cls: self._dispatch_to_handler})

    def _dispatch_to_handler(self, cmd):
        cmd_name = cmd.__class__.__name__
        handler_name = re.sub("([A-Z]+)", r"_\1", cmd_name).lower()
        try:
            getattr(self, handler_name)(cmd)
        except Exception as e:
            self._abort_operation(cmd, str(e))

    def _abort_operation(self, cmd, error: str):
        self._evt_dispatcher.dispatch(OperationError(cmd, error))

    def _start_transaction(self, repo, cmd_id, impl, *args):
        retry_count = 5
        while retry_count > 0:
            context = repo.make_context()
            try:
                impl(context, *args)
                models = context.entities()
                models_events = []
                for model in models:
                    events = model.release_events()
                    models_events.append(
                        [evtcls(cmd_id, *events[evtcls]) for evtcls in events]
                    )

                context.commit()
                retry_count = 0
                for model_events in models_events:
                    for event in model_events:
                        self._evt_dispatcher.dispatch(event)
            except RepoError as e:
                self._logger.error("Repo error", error=e)
                retry_count -= 1
                # TODO: differenciate fatal from non fatal errors
