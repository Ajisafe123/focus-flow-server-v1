import pkgutil
import importlib
import pathlib

from src.models.hadith import Hadith

__all__ = ["Hadith"]


# Dynamically import all modules in this package (src/models)
package_dir = pathlib.Path(__file__).resolve().parent

for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
    importlib.import_module(f"{__package__}.{module_name}")
