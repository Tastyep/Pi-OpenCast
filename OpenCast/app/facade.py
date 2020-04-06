from OpenCast.domain.event.dispatcher import EventDispatcher

from .command.dispatcher import CommandDispatcher


class AppFacade:
    def __init__(self):
        self._cmd_dispatcher = CommandDispatcher()
        self._evt_dispatcher = EventDispatcher()

    def cmd_dispatcher(self):
        return self._cmd_dispatcher

    def evt_dispatcher(self):
        return self._evt_dispatcher
