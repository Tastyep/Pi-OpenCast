from unittest.mock import Mock


class AppFacadeMock(Mock):
    def __init__(self):
        super(AppFacadeMock, self).__init__()
        self.cmd_dispatcher = Mock()
        self.evt_dispatcher = Mock()
        self.workflow_manager = Mock()
        self.workflow_factory = Mock()
