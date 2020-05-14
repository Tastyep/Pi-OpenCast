def to_camelcase(name):
    return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")
