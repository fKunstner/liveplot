"""Code loading module and utilities."""
import inspect
import logging
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("liveplot.code_loader")


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
    logger.debug("Importing module.")

    if not file_path.is_file():
        raise FileNotFoundError(
            f"File {file_path} not found when trying to load module."
        )

    spec = spec_from_file_location("module.name", file_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import module in file path '{file_path}'.")

    module = module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except SyntaxError as exc:
        raise ImportError(
            f"Could not import module in file path '{file_path}' "
            f"due to syntax error."
        ) from exc
    except Exception as exc:
        raise ImportError(
            f"Could not import module in file path '{file_path}' "
            f"due to an error on execution."
        ) from exc

    return module


def _except_exec(func, *args, **kwargs):
    """Log any exception thrown by func (except Interrupts and SystemExit).

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


def _file_modified_date(file_path):
    return file_path.stat().st_mtime


class ModuleLoader:
    """Wrap a module to reload it on demand.

    If ``patch_if_missing`` is given, patches the functions (keys, strings)
    with the given dummy implementation (value, Callable).

    Args:
        file_path: The module file path to load
        patch_if_missing: A list of function names and dummy callables
            to patch if missing.
    """

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

    def load_module(self) -> None:
        """Load (or reload) the module.

        Raises:
            ImportError if the module could not be reloaded.
        """
        logger.debug(f"Loading module at {self._file_path}.")

        self._module = _import_module(self._file_path)
        self._loast_load = _except_exec(_file_modified_date, self._file_path)

        if self._patch_if_missing is not None:
            self._module = self._patch_missing_functions(
                self._module, self._patch_if_missing
            )

    @staticmethod
    def _patch_missing_functions(module, patches: Dict[str, Callable]):
        patched = []
        for f_name, func in patches.items():
            if not hasattr(module, f_name):
                setattr(module, f_name, func)
                patched.append(f_name)
        logger.info(
            f"The functions {patched} were not found "
            f"and have been patched with default behavior."
        )
        return module

    def _save_function_source(self, f_name: str):
        source = _except_exec(inspect.getsource, getattr(self._module, f_name))
        self._functions_source_last_exec[f_name] = source

    def func_has_changed(self, f_name: str) -> bool:
        """Check if the function has changed since its last call.

        Compares the source when last called to the source in memory.

        Raises:
            ValueError if the function has never been called.
        """
        source = _except_exec(inspect.getsource, getattr(self._module, f_name))
        if f_name not in self._functions_source_last_exec:
            raise ValueError(
                f"Asked if function '{f_name}' has changed "
                f"but '{f_name}' was never executed."
            )
        return self._functions_source_last_exec[f_name] != source

    def call(self, f_name: str, *args, **kwargs) -> Any:
        """Call the function ``f_name`` and passes it all other arguments.

        Saves the function source for future comparison in
        :func:`~CodeLoader.func_has_changed`.
        """
        logger.debug(f"Executing function {f_name}.")
        self._save_function_source(f_name)
        return _except_exec(getattr(self._module, f_name), *args, **kwargs)

    def file_has_changed(self) -> bool:
        """Whether the file has changed on disk since its last load.

        Compares the last load time with the file's last modified (``st_mtime``).
        """
        return self._loast_load != _except_exec(_file_modified_date, self._file_path)
