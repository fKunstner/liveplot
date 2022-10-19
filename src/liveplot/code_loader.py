import inspect
import logging
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("liveplot")


def _import_module(file_path: Path):
    logger.debug(f"Importing module.")
    spec = spec_from_file_location("module.name", file_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import module in file path '{file_path}'.")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def except_exec(func, *args, **kwargs):
    """
    logger.any exception thrown by func (except Interrupts and SystemExit).
    Returns the value of func(*args, **kwargs) if successful, None otherwise.
    """
    # noinspection PyBroadException
    try:
        return func(*args, **kwargs)
    except Exception:
        logger.exception(
            f"Code triggered an exception. "
            f"Will try to recover. "
            f"Initial error in {func.__name__}: {func}."
        )
        return None


def file_modified_date(file_path):
    return file_path.stat().st_mtime


class CodeLoader:
    """Wraps a module and reloads it on demand."""

    def __init__(
        self,
        file_path: Path,
        patch_if_missing: Optional[Dict[str, Callable]] = None,
    ):
        logger.debug(f"Creating CodeLoader for {file_path}.")
        self._file_path: Path = file_path
        self._patch_if_missing = patch_if_missing
        self._functions_source_last_exec: Dict[str, Any] = {}
        self._module = None
        self._loast_load = None

    def load_module(self):
        logger.debug(f"Loading module at {self._file_path}.")

        self._module = _import_module(self._file_path)
        self._loast_load = except_exec(file_modified_date, self._file_path)

        if self._patch_if_missing is not None:
            for f_name, func in self._patch_if_missing.items():
                if not hasattr(self._module, f_name):
                    setattr(self._module, f_name, func)
                    logger.warning(
                        f"Function {f_name} not found. Patching with default."
                    )

    def _save_function_source(self, f_name: str):
        source = except_exec(inspect.getsource, getattr(self._module, f_name))
        self._functions_source_last_exec[f_name] = source

    def func_has_changed(self, f_name: str):
        """Checks if a function has changed since its last call.

        Compares the source of the function when it was last called
        and the source of the function in the module in memory.

        Call ``load_module`` to reload from disk.

        Raises:
            ValueError if the function ``f_name`` has never been called.
        """
        source = except_exec(inspect.getsource, getattr(self._module, f_name))
        if f_name not in self._functions_source_last_exec:
            raise ValueError(
                f"Asked if function '{f_name}' has changed "
                f"but '{f_name}' was never executed."
            )
        return self._functions_source_last_exec[f_name] != source

    def call(self, f_name: str, *args, **kwargs):
        logger.debug(f"Executing function {f_name}.")
        self._save_function_source(f_name)
        return except_exec(getattr(self._module, f_name), *args, **kwargs)

    def file_has_changed(self):
        return self._loast_load != except_exec(file_modified_date, self._file_path)
