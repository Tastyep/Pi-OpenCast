import logging


class EventDispatcher:
    class _Handler:
        def __init__(self, functor, count=-1):
            self._functor = functor
            self._count = count

        def __call__(self, *args):
            self._functor(*args)
            if self._count > 0:
                self._count -= 1

        def expired(self):
            return self._count == 0

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._handlers_map = {}

    def attach(self, evt, handler):
        self._attach(evt, self._Handler(handler))

    def on(self, evt, callback):
        self._attach(evt, self._Handler(callback, 1))

    def dispatch(self, evt):
        self._logger.debug(f"raising: {evt}")
        evt_id = id(type(evt))
        if evt_id in self._handlers_map:
            handlers = self._handlers_map[evt_id]
            for handler in handlers[:]:
                handler(evt)
                if handler.expired():
                    handlers.remove(handler)

    def _attach(self, evt, handler):
        evt_id = id(evt)
        if evt_id not in self._handlers_map:
            self._handlers_map[evt_id] = list()
        self._handlers_map[evt_id].append(handler)
