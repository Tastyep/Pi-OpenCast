import inspect
import re

from OpenCast.infra.data.repo.error import RepoError
from OpenCast.infra.media.error import PlayerError


class Service:
    def __init__(self, app_facade, logger, derived, cmd_module, evt_module=None):
        self._cmd_dispatcher = app_facade.cmd_dispatcher()
        self._evt_dispatcher = app_facade.evt_dispatcher()
        self._logger = logger
        self.__derived = derived
        self._register_handlers(self._cmd_dispatcher, cmd_module)
        if evt_module is not None:
            self._register_handlers(self._evt_dispatcher, evt_module)

    def _register_handlers(self, dispatcher, module):
        classes = inspect.getmembers(module, inspect.isclass)
        for _, cls in classes:
            if cls.__module__ == module.__name__:
                self._register_handler(dispatcher, cls)

    def _register_handler(self, dispatcher, cls):
        cls_name = cls.__name__
        handler_name = re.sub("([A-Z]+)", r"_\1", cls_name).lower()
        try:
            handler = getattr(self.__derived, handler_name)
            dispatcher.observe(cls, handler)
        except AttributeError:
            self._logger.error(f"No handler '{handler_name}' found for '{cls_name}'")
            # Raise the exception as it is a developer error
            raise

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
            except (RepoError, PlayerError) as e:
                self._logger.error(f"caught repo error: {e}")
                retry_count -= 1
                # TODO: differenciate fatal from non fatal errors
