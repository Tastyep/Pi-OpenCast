import logging
from threading import Lock


class EventDispatcher:
    class _Handler:
        def __init__(self, functor, count):
            self._functor = functor
            self._count = count

        def __call__(self, *args):
            self._functor(*args)
            if self._count > 0:
                self._count -= 1

        def expired(self):
            return self._count == 0

    def __init__(self, executor):
        self._logger = logging.getLogger(__name__)
        self._executor = executor
        self._handlers_map = {}
        self._lock = Lock()

    def observe(self, evt_cls, handler, times=-1):
        self._observe(evt_cls, None, self._Handler(handler, times))

    def once(self, evt_cls, handler):
        self.observe(evt_cls, handler, 1)

    def observe_id(self, evt_cls, evt_id, handler, times=-1):
        self._observe(evt_cls, evt_id, self._Handler(handler, times))

    def dispatch(self, evt):
        def impl(evt):
            self._logger.debug(f"raising: {evt}")

            evt_cls = type(evt)
            handlers = []
            with self._lock:
                if evt_cls not in self._handlers_map:
                    return

                evt_handlers_map = self._handlers_map[evt_cls]
                for evt_id in set([None, evt.id]):
                    if evt_id in evt_handlers_map:
                        handlers = [*handlers, *evt_handlers_map[evt_id]]

            if not handlers:
                return
            for handler in handlers:
                handler(evt)

            with self._lock:
                evt_handlers_map = self._handlers_map[evt_cls]
                for evt_id in set([None, evt.id]):
                    if evt_id in evt_handlers_map:
                        for handler in list(evt_handlers_map[evt_id]):
                            if handler.expired():
                                evt_handlers_map[evt_id].remove(handler)

        self._executor.submit(impl, evt)

    def _observe(self, evt_cls, evt_id, handler):
        if evt_cls not in self._handlers_map:
            self._handlers_map[evt_cls] = {evt_id: []}
        id_to_handlers = self._handlers_map.get(evt_cls, {evt_id: []})
        handlers = id_to_handlers.get(evt_id, [])
        handlers.append(handler)
        self._handlers_map[evt_cls][evt_id] = handlers
