import importlib
import inspect
import sys
from os import getenv
from pkgutil import iter_modules


def models():
    _models = []

    module = sys.modules[__name__]
    prefix = f"{module.__name__}."
    for loader, submodule_name, _ in iter_modules(module.__path__, prefix):
        submodule = importlib.import_module(submodule_name, loader.path)
        for name, obj in inspect.getmembers(submodule, inspect.isclass):
            _models.append(obj)

    return _models


__models__ = models()


TORTOISE_CONFIG = {
    "connections": {
        "default": getenv("DATABASE_URI"),
    },
    "apps": {
        "models": {
            "models": ["jeopardy.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
