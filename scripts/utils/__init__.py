import json


class DotDict(dict):
    """Python dictionary you can access via dot notation."""

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, "keys"):
                value = DotDict(value)
            self[key] = value


def load_config(file):
    return DotDict(json.load(file))