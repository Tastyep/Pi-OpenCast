import dataclasses
import inspect
import re

from OpenCast.infra.data.repo.error import RepoError


class Service(object):
    def __init__(self, app_facade, logger, derived, cmd_module, evt_module=None):
        self._cmd_dispatcher = app_facade.cmd_dispatcher()
        self._evt_dispatcher = app_facade.evt_dispatcher()
        self._logger = logger
        self.__derived = derived
        self._register_handlers(self._cmd_dispatcher, cmd_module)
        if evt_module is not None:
            self._register_handlers(self._evt_dispatcher, evt_module)

    def _register_handlers(self, dispatcher, module):
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if dataclasses.is_dataclass(obj):
                self._register_handler(dispatcher, obj)

    def _register_handler(self, dispatcher, obj):
        handler_name = re.sub("([A-Z]+)", r"_\1", obj.__name__).lower()
        try:
            handler = getattr(self.__derived, handler_name)
            dispatcher.attach(obj, handler)
        except AttributeError:
            self._logger.error(
                "No handler '{}' found for '{}'".format(handler_name, obj.__name__)
            )
            # Raise the exception as it is a developer error
            raise

    def _start_transation(self, repo, impl):
        retry = True
        while retry:
            context = repo.make_context()
            try:
                impl(context)
                models = context.commit()
                retry = False
                for model in models:
                    events = model.release_events()
                    for evt in events:
                        self._evt_dispatcher.dispatch(evt)
            except RepoError as e:
                self._logger.error("caught repo error: {}".format(e))
                # TODO: differenciate fatal from non fatal errors
