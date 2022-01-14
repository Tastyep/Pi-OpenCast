from dataclasses import dataclass
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.domain.event.dispatcher import EventDispatcher
from OpenCast.domain.event.event import Event
from OpenCast.domain.service.identity import IdentityService


@dataclass
class DummyEvent(Event):
    pass


class EventDispatcherTest(TestCase):
    def setUp(self):
        self.dispatcher = EventDispatcher()
        self.cmd_id = IdentityService.random()
        self.evt = Mock()
        self.evt.id = self.cmd_id
        self.handler = Mock()

    def test_observe_event(self):
        self.dispatcher.observe({type(self.evt): self.handler})

        self.dispatcher.dispatch(self.evt)
        self.handler.assert_called_once_with(self.evt)

    def test_observe_event_by_id(self):
        self.dispatcher.observe_result(self.cmd_id, {type(self.evt): self.handler})
        # Unrelated event should not call the handler
        self.dispatcher.observe_result(
            IdentityService.random(), {type(self.evt): self.handler}
        )

        self.dispatcher.dispatch(self.evt)
        self.handler.assert_called_once_with(self.evt)

    def test_observe_event_once(self):
        self.dispatcher.once(type(self.evt), self.handler)

        self.dispatcher.dispatch(self.evt)
        self.handler.assert_called_once_with(self.evt)

        self.handler.reset_mock()
        self.dispatcher.dispatch(self.evt)
        self.handler.assert_not_called()

    def test_observe_same_event_multiple_times_same_source(self):
        id_handler = Mock()
        self.dispatcher.observe_result(
            self.cmd_id, {type(self.evt): id_handler}, times=1
        )
        self.dispatcher.observe_result(
            self.cmd_id, {type(self.evt): self.handler}, times=1
        )

        self.dispatcher.dispatch(self.evt)
        id_handler.assert_called_once_with(self.evt)
        self.handler.assert_called_once_with(self.evt)
        id_handler.reset_mock()
        self.handler.reset_mock()

        self.dispatcher.dispatch(self.evt)
        id_handler.assert_not_called()
        self.handler.assert_not_called()

    def test_observe_same_event_multiple_times_diff_source(self):
        id_handler = Mock()
        self.dispatcher.observe_result(
            self.cmd_id, {type(self.evt): id_handler}, times=1
        )
        self.dispatcher.observe({type(self.evt): self.handler})

        self.dispatcher.dispatch(self.evt)
        id_handler.assert_called_once_with(self.evt)
        self.handler.assert_called_once_with(self.evt)
        id_handler.reset_mock()
        self.handler.reset_mock()

        self.dispatcher.dispatch(self.evt)
        id_handler.assert_not_called()
        self.handler.assert_called_once_with(self.evt)

    def test_observe_group(self):
        cmd_id = IdentityService.random()
        handler = Mock()
        event = DummyEvent(cmd_id, IdentityService.random())
        self.dispatcher.observe_group(
            {
                self.cmd_id: {type(self.evt): self.handler},
                cmd_id: {type(event): handler},
            },
            times=1,
        )

        self.dispatcher.dispatch(self.evt)
        handler.assert_not_called()
        self.handler.assert_called_once_with(self.evt)
        handler.reset_mock()
        self.handler.reset_mock()

        self.dispatcher.dispatch(event)
        handler.assert_not_called()
        self.handler.assert_not_called()

    def test_observe_group_reverse(self):
        cmd_id = IdentityService.random()
        handler = Mock()
        event = DummyEvent(cmd_id, IdentityService.random())
        self.dispatcher.observe_group(
            {
                self.cmd_id: {type(self.evt): self.handler},
                cmd_id: {type(event): handler},
            },
            times=1,
        )

        self.dispatcher.dispatch(event)
        handler.assert_called_once_with(event)
        self.handler.assert_not_called()
        handler.reset_mock()
        self.handler.reset_mock()

        self.dispatcher.dispatch(self.evt)
        handler.assert_not_called()
        self.handler.assert_not_called()
