from OpenCast.domain.service.identity import IdentityService


class Controller:
    def __init__(self, app_facade):
        self._cmd_dispatcher = app_facade.cmd_dispatcher()
        self._evt_dispatcher = app_facade.evt_dispatcher()

    def _dispatch(self, cmd_cls, component_id, *args, **kwargs):
        cmd_id = IdentityService.id_command(cmd_cls, component_id)
        self._cmd_dispatcher.dispatch(cmd_cls(cmd_id, component_id, *args, **kwargs))
