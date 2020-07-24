from OpenCast.domain.service.identity import IdentityService


def make_cmd(cmd_cls, model_id, *args, **kwargs):
    cmd_id = IdentityService.id_command(cmd_cls, model_id)
    return cmd_cls(cmd_id, model_id, *args, **kwargs)
