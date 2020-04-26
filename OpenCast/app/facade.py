from concurrent.futures import ThreadPoolExecutor

from OpenCast.domain.event.dispatcher import EventDispatcher

from .command.dispatcher import CommandDispatcher


class AppFacade:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1)  # TODO: make configurable
        self._cmd_dispatcher = CommandDispatcher(self._executor)
        self._evt_dispatcher = EventDispatcher(self._executor)

    def cmd_dispatcher(self):
        return self._cmd_dispatcher

    def evt_dispatcher(self):
        return self._evt_dispatcher
