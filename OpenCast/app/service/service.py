import dataclasses
import inspect
import re


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

    def _register_handlers(self, cmd_handlers):
        for cmd, handler in cmd_handlers.items():
            self._cmd_dispatcher.attach(cmd, handler)
