from collections import namedtuple
from unittest.mock import Mock

from OpenCast.domain.service.identity import IdentityService


class EventExpecter:
    _HandlerData = namedtuple("HandlerData", ["functor", "attrs", "dict_attrs"])

    def __init__(self, cmd_dispatcher, evt_dispatcher):
        self.cmd_dispatcher = cmd_dispatcher
        self.evt_dispatcher = evt_dispatcher
        self.evt_to_handler = {}

    def from_(self, cmd_cls, model_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, model_id)

        for evt_cls, handler_data in self.evt_to_handler.items():
            self.evt_dispatcher.observe_result(cmd_id, {evt_cls: handler_data.functor})

        cmd = cmd_cls(cmd_id, model_id, *args, **kwargs)
        self.cmd_dispatcher.dispatch(cmd)

        for evt_cls, handler_data in self.evt_to_handler.items():
            handler_data.functor.assert_called_once_with(
                evt_cls(cmd_id, *handler_data.attrs, **handler_data.dict_attrs)
            )

    def from_event(self, evt_cls, model_id, *args, **kwargs):
        cmd_id = IdentityService.random()

        for cls, handler_data in self.evt_to_handler.items():
            self.evt_dispatcher.observe_result(cmd_id, {cls: handler_data.functor})

        evt = evt_cls(cmd_id, model_id, *args, **kwargs)
        self.evt_dispatcher.dispatch(evt)

        for cls, handler_data in self.evt_to_handler.items():
            handler_data.functor.assert_called_once_with(
                cls(cmd_id, *handler_data.attrs, **handler_data.dict_attrs)
            )

    def expect(self, evt_cls, *args, **kwargs):
        handler_mock = Mock()
        self.evt_to_handler[evt_cls] = self._HandlerData(handler_mock, args, kwargs)
        return self
