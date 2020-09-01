from test.util import TestCase
from unittest.mock import Mock
from uuid import uuid4

from OpenCast.domain.event.dispatcher import EventDispatcher


class EventDispatcherTest(TestCase):
    def setUp(self):
        self.dispatcher = EventDispatcher()
        self.cmd_id = uuid4()
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
        self.dispatcher.observe_result(uuid4(), {type(self.evt): self.handler})
        self.dispatcher.dispatch(self.evt)
        self.handler.assert_called_once_with(self.evt)

    def test_observe_event_once(self):
        self.dispatcher.once(type(self.evt), self.handler)
        self.dispatcher.dispatch(self.evt)
        self.handler.assert_called_once_with(self.evt)

        self.handler.reset_mock()
        self.dispatcher.dispatch(self.evt)
        self.handler.assert_not_called()

    def test_multiple_observe_event(self):
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
