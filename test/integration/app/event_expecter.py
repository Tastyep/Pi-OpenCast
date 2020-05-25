from collections import namedtuple
from unittest.mock import Mock

from OpenCast.app.service.error import OperationError
from OpenCast.domain.event.event import Event as DomainEvent
from OpenCast.domain.service.identity import IdentityService


class EventExpecter:
    _HandlerData = namedtuple("HandlerData", ["functor", "attrs"])

    def __init__(self, cmd_dispatcher, evt_dispatcher):
        self.cmd_dispatcher = cmd_dispatcher
        self.evt_dispatcher = evt_dispatcher
        self.evt_to_handler = {}

    def from_(self, cmd_cls, model_id, *args):
        cmd_id = IdentityService.id_command(cmd_cls, model_id)

        for evt_cls, handler_data in self.evt_to_handler.items():
            self.evt_dispatcher.observe(cmd_id, {evt_cls: handler_data.functor})

        cmd = cmd_cls(cmd_id, model_id, *args)
        self.cmd_dispatcher.dispatch(cmd)

        for evt_cls, handler_data in self.evt_to_handler.items():
            if issubclass(evt_cls, DomainEvent):
                handler_data.functor.assert_called_once_with(
                    evt_cls(cmd_id, model_id, *handler_data.attrs)
                )
            elif issubclass(evt_cls, OperationError):
                handler_data.functor.assert_called_once_with(
                    evt_cls(cmd_id, *handler_data.attrs)
                )

    def expect(self, evt_cls, *args):
        handler_mock = Mock()
        self.evt_to_handler[evt_cls] = self._HandlerData(handler_mock, args)
        return self
