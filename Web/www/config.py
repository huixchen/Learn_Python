from config_default import configs


def merge(default, override):
    r = {}
    for k, v in default.items():
        if k in override.keys():
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


class Dict(dict):
    # dict support access as x.y style
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"Dict object has not attribute {}".format(key))

    def __setattr__(self, key, value):
        self[key] = value


def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D


try:
    import config_overide
    configs = merge(configs, config_overide)
except ImportError:
    pass

configs = toDict(configs)
