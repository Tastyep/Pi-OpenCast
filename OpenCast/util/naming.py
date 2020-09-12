""" Utilities related to the project's naming conventions """


def to_camelcase(name):
    return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")


def name_factory_method(cls):
    return f"make_{to_camelcase(cls.__name__)}"


def name_handler_method(cls, private=True):
    name = to_camelcase(cls.__name__)
    return name if not private else f"_{name}"
