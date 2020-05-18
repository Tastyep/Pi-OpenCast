import structlog


class CommandDispatcher:
    def __init__(self, executor):
        self._logger = structlog.get_logger(__name__)
        self._executor = executor
        self._handlers_map = {}

    def observe(self, cmd_cls, handler):
        cmd_id = id(cmd_cls)
        if cmd_id not in self._handlers_map:
            self._handlers_map[cmd_id] = list()
        self._handlers_map[cmd_id].append(handler)

    def dispatch(self, cmd):
        def impl(cmd):
            self._logger.debug(type(cmd).__name__, cmd=cmd)
            cmd_id = id(type(cmd))
            if cmd_id in self._handlers_map:
                handlers = self._handlers_map[cmd_id]
                for handler in handlers:
                    handler(cmd)

        self._executor.submit(impl, cmd)
