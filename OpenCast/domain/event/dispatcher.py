""" Dispatch events to handlers """

from copy import deepcopy
from threading import Lock

import structlog

from OpenCast.infra import Id


class EventDispatcher:
    ANY_ID = None

    class _Handler:
        def __init__(self, evtcls_handler, count):
            self._evtcls_handler = evtcls_handler
            self._count = count

        def __call__(self, evt, *args):
            self._evtcls_handler[type(evt)](evt, *args)

        def handled_evts(self):
            return self._evtcls_handler.keys()

        def update_expires(self):
            if self._count > 0:
                self._count -= 1

            return self._count == 0

    def __init__(self):
        self._logger = structlog.get_logger(__name__)
        self._handler_map = {}
        self._evt_to_handler_ids = {}
        self._lock = Lock()

    def once(self, evt_cls, handler):
        self.observe_result(self.ANY_ID, {evt_cls: handler}, 1)

    def observe(self, evtcls_handler: dict, times=-1):
        self.observe_result(self.ANY_ID, evtcls_handler, times)

    def observe_result(self, evt_id: Id, evtcls_handler: dict, times=-1):
        self._observe(
            evt_id, evtcls_handler.keys(), self._Handler(evtcls_handler, times)
        )

    def dispatch(self, evt):
        def remove_handler_links(evt_id, handler):
            handler_id = id(handler)
            for evt_cls in handler.handled_evts():
                evt_hash = hash((evt_id, evt_cls))
                self._evt_to_handler_ids[evt_hash].remove(handler_id)
            self._handler_map.pop(handler_id)

        self._logger.debug(type(evt).__name__, evt=evt)

        handlers = []
        with self._lock:
            for evt_id in set([self.ANY_ID, evt.id]):
                evt_hash = hash((evt_id, type(evt)))
                if evt_hash not in self._evt_to_handler_ids:
                    continue

                handler_ids = deepcopy(self._evt_to_handler_ids[evt_hash])
                for handler_id in handler_ids:
                    handler = self._handler_map[handler_id]
                    handlers.append(handler)
                    if handler.update_expires():
                        remove_handler_links(evt_id, handler)

        for handler in handlers:
            handler(evt)

    def _observe(self, evt_id: Id, evt_clss: list, handler):
        with self._lock:
            handler_id = id(handler)
            self._handler_map[handler_id] = handler

            for evt_cls in evt_clss:
                evt_hash = hash((evt_id, evt_cls))
                handler_ids = self._evt_to_handler_ids.get(evt_hash, [])
                handler_ids.append(handler_id)
                self._evt_to_handler_ids[evt_hash] = handler_ids
