""" Structural representation of an applicative order """


from OpenCast.domain.service.identity import IdentityService


def make_cmd(cmd_cls, model_id, *args, **kwargs):
    """Command factory method.

    Args:
        cmd_cls: The class of the command.
        model_id: The ID of the related model.
        *args: Variable length argument list, forwarded to the command's constructor
        **kwargs: Arbitrary keyword arguments, forwarded to the command's constructor

    Returns:
        Command: The created command.
    """
    cmd_id = IdentityService.id_command(cmd_cls, model_id)
    return cmd_cls(cmd_id, model_id, *args, **kwargs)
