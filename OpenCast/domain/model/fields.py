""" Custom fields used by model's schema definitions """

import typing
from pathlib import Path

from marshmallow.fields import Field


class PathField(Field):
    """A path field."""

    #: Default error messages.
    default_error_messages = {
        "invalid": "Not a valid path.",
    }

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[Path]:
        if value is None:
            return None
        if not isinstance(value, Path):
            raise self.make_error("invalid")
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        if value is None:
            return None
        return Path(value)
