""" Monitoring data schemas """

from marshmallow import Schema, fields
from marshmallow.fields import List, Nested
from marshmallow.schema import SchemaMeta

from OpenCast.domain.model.video import VideoSchema


class Videos(Schema):
    videos = fields.List(fields.Nested(VideoSchema))


class ErrorSchema(Schema):
    message = fields.String()
    details = fields.Dict(keys=fields.String(), values=fields.String())


def schema(**kwargs):
    items = list(kwargs.items())
    if len(items) != 1 or not isinstance(items[0][1], dict):
        raise RuntimeError("schema required 1 keyword argument of type dict")
    name, spec = items[0]

    schema_dict = {}
    for key, value in spec.items():
        cls, description = value if isinstance(value, tuple) else (value, None)
        required = key.endswith("*")
        key = key.rstrip("*")
        kwargs = {"required": required, "description": description}

        if isinstance(cls, SchemaMeta):
            schema_dict[key] = Nested(cls, required=required)
        elif isinstance(cls, list) and len(cls) == 1:
            cls = cls[0]
            schema_dict[key] = (
                List(Nested(cls), **kwargs)
                if isinstance(cls, SchemaMeta)
                else List(cls, **kwargs)
            )
        else:
            schema_dict[key] = cls.__call__(**kwargs) if callable(cls) else cls
    return type(name, (Schema,), schema_dict)
