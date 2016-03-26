from importlib import import_module

def import_obj(path):
    parts = path.split('.')
    module_path = '.'.join(parts[:-1])
    class_name = parts[-1]
    m = import_module(module_path)
    obj = getattr(m, class_name)
    return obj
