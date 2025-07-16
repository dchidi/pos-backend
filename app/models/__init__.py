import inspect
import importlib.util
import sys
from pathlib import Path
from beanie import Document

MODELS = []

models_dir = Path(__file__).parent

for path in models_dir.rglob("*.py"):
    if path.name in ("__init__.py", "base.py"):
        continue

    module_path = path.with_suffix("").relative_to(models_dir.parent)
    # module_name = ".".join(module_path.parts)
    module_name = "app." + ".".join(module_path.parts)   # ➜ "app.models.brand"

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Document) and obj is not Document:
                MODELS.append(obj)
                globals()[name] = obj

MODELS = tuple(MODELS)
# print("MODELS:", [m.__module__ + "." + m.__name__ for m in MODELS])
__all__ = [m.__name__ for m in MODELS]
