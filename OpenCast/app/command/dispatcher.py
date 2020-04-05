import logging


class CommandDispatcher:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._handlers_map = {}

    def attach(self, cmd, handler):
        cmd_id = id(cmd)
        if cmd_id not in self._handlers_map:
            self._handlers_map[cmd_id] = list()
        self._handlers_map[cmd_id].append(handler)

    def dispatch(self, cmd):
        self._logger.debug(f"dispatching: {cmd}")
        cmd_id = id(type(cmd))
        if cmd_id in self._handlers_map:
            handlers = self._handlers_map[cmd_id]
            for handler in handlers:
                handler(cmd)
