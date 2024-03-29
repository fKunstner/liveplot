"""Code loading module and utilities."""
import inspect
import logging
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("liveplot.code_loader")


# pylint: disable=missing-docstring
def dummy_load_data():
    return None


# noinspection PyUnusedLocal
# pylint: disable=missing-docstring,unused-argument
def dummy_postprocess(data):
    return data


# noinspection PyUnusedLocal
# pylint: disable=missing-docstring,unused-argument
def dummy_make_figure(fig, data):
    return None


# noinspection PyUnusedLocal
# pylint: disable=missing-docstring,unused-argument
def dummy_settings(plt):
    return None


possible_patches = {
    "load_data": dummy_load_data,
    "postprocess": dummy_postprocess,
    "settings": dummy_settings,
    "make_figure": dummy_make_figure,
}


def _patch_missing_functions(module):
    patched = []
    for f_name, func in possible_patches.items():
        if not hasattr(module, f_name):
            setattr(module, f_name, func)
            patched.append(f_name)

    if len(patched) > 0:
        message = (
            f"The functions {patched} were "
            if len(patched) > 1
            else f"The function {patched} was "
        )
        logger.info(message + "not found and patched with default behavior")

    return module


def _import_module(file_path: Path):
    """Import a module by filepath.

    Args:
        file_path: The path to load

    Returns:
        The loaded python module

    Raises:
        ImportError if the module could not be found,
        including if the filepath
        does not exist
    """
    logger.debug("Importing module")

    if not file_path.is_file():
        raise FileNotFoundError(
            f"File {file_path} not found when trying to load module."
        )

    spec = spec_from_file_location(f"UserPlottingCode.{file_path.stem}", file_path)

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not import module in file path '{file_path}'"
            f"but unclear what could go wrong to trigger this"
        )

    module = module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ImportError(f"Could not import module in file '{file_path}'") from exc

    return module


class PlottingModuleError(Exception):
    """Base class to wrap exceptions occuring in module code."""

    def __init__(self, *args):
        super().__init__(*args)


class ModuleLoader:
    """Wrap a module to reload it on demand.

    If ``patch_if_missing`` is given, patches the functions (keys, strings)
    with the given dummy implementation (value, Callable).

    Args:
        file_path: The module file path to load
    """

    def __init__(
        self,
        file_path: Path,
    ):
        logger.debug(f"Creating CodeLoader for {file_path}")
        self._file_path: Path = file_path
        self._functions_source_last_exec: Dict[str, Any] = {}
        self._module = None
        self._last_load_attempt: Optional[float] = None

    def load_module(self) -> None:
        """Load (or reload) the module.

        Raises:
            ImportError if the module could not be reloaded.
        """
        logger.debug(f"Loading module at {self._file_path}")
        self._last_load_attempt = self._file_path.stat().st_mtime
        self._module = _import_module(self._file_path)
        self._module = _patch_missing_functions(self._module)

    def _save_function_source(self, f_name: str):
        source = inspect.getsource(getattr(self._module, f_name))
        self._functions_source_last_exec[f_name] = source

    def func_has_changed(self, f_name: str) -> bool:
        """Check if the function has changed since its last call.

        Compares the source when last called to the source in memory.

        Raises:
            ValueError if the function has never been called.
        """
        never_executed = f_name not in self._functions_source_last_exec
        source = inspect.getsource(getattr(self._module, f_name))
        return never_executed or self._functions_source_last_exec[f_name] != source

    def call(self, f_name: str, *args, **kwargs) -> Any:
        """Call the function ``f_name`` and passes it all other arguments.

        Saves the function source for future comparison in
        :func:`~CodeLoader.func_has_changed`.
        """
        logger.debug(f"Executing function {f_name}")
        self._save_function_source(f_name)
        func = getattr(self._module, f_name)
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            raise PlottingModuleError(
                f"Plotting triggered an exception in `{f_name}`, trying to recover"
            ) from exc

    def should_reload(self) -> bool:
        """Whether the file has changed on disk since its last load.

        Compares the last load time with the file's last modified (``st_mtime``).
        """
        return (
            self._last_load_attempt is None
            or self._last_load_attempt < self._file_path.stat().st_mtime
        )
