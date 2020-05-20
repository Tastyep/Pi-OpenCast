from test.util import TestCase
from unittest.mock import Mock

from OpenCast.app.command.dispatcher import CommandDispatcher


class CommandDispatcherTest(TestCase):
    def setUp(self):
        def execute_handler(executor, handler, *args):
            handler(*args)

        self.evt_loop = Mock()
        self.evt_loop.run_in_executor = Mock(side_effect=execute_handler)

        self.dispatcher = CommandDispatcher(self.evt_loop)
        self.cmd = Mock()
        self.handler = Mock()

    def test_observe_command(self):
        self.dispatcher.observe(type(self.cmd), self.handler)
        self.dispatcher.dispatch(self.cmd)
        self.handler.assert_called_once_with(self.cmd)

    def test_multiple_observe_command(self):
        other_handler = Mock()
        self.dispatcher.observe(type(self.cmd), self.handler)
        self.dispatcher.observe(type(self.cmd), other_handler)
        self.dispatcher.dispatch(self.cmd)

        self.handler.assert_called_once_with(self.cmd)
        other_handler.assert_called_once_with(self.cmd)
