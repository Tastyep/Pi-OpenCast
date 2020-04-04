class Controller(object):
    def __init__(self, app_facade):
        self._cmd_dispatcher = app_facade.cmd_dispatcher()
        self._evt_dispatcher = app_facade.evt_dispatcher()
