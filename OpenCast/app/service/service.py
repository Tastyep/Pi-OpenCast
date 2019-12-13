import inspect
import re


class Service(object):
    def __init__(self, cmd_dispatcher, logger, derived, cmd_module):
        for name, obj in inspect.getmembers(cmd_module):
            if inspect.isclass(obj):
                handler_name = re.sub('([A-Z]+)', r'_\1', obj.__name__).lower()
                try:
                    handler = getattr(derived, handler_name)
                    cmd_dispatcher.attach(obj, handler)
                except AttributeError as e:
                    logger.error(
                        "No handler '{}' found for command '{}'".format(
                            handler_name, obj.__name__
                        )
                    )
                    # Raise the exception as it is a developer error
                    raise

    def _register_handlers(self, cmd_handlers):
        for cmd, handler in cmd_handlers.items():
            self._cmd_dispatcher.attach(cmd, handler)
