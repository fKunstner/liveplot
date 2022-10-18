import inspect
import logging
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import PurePath
from types import ModuleType
from typing import Callable, Dict, Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing_extensions import Literal, get_args

FuncName = Literal["load_data", "make_figure", "settings"]


logger = logging.getLogger("liveplot")


def file_modified_date(file_path):
    return file_path.stat().st_mtime


# noinspection PyUnusedLocal
def dummy_noop(*args, **kwargs):
    pass


def dummy_identity(x):
    return x


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


class WrappedFig:
    """Wraps a matplotlib figure, holds interactive element and quits on close."""

    def __init__(self):
        self.fig: Optional[Figure] = None
        self._close_handler: Optional[Callable] = None

    def new_figure(self):
        self.fig = plt.figure()
        self._close_handler: Optional[Callable] = self.fig.canvas.mpl_connect(
            "close_event", lambda event: sys.exit()
        )
        plt.show(block=False)

    def close_without_exit(self):
        if self.fig is not None:
            self.fig.canvas.mpl_disconnect(self._close_handler)
            plt.close(self.fig)


class PlottingCode:
    """Wraps the module passed by the user and reloads components on demand."""

    def __init__(self, file_path: PurePath):
        logger.debug(f"Creating PlottingCode object for {file_path}.")
        self._file_path: PurePath = file_path
        self._functions_source_last_exec: Dict[FuncName, Optional] = {}
        self._module: Optional[ModuleType] = None
        self._last_change = None

    def load_module(self):
        logger.debug(f"Loading module at {self._file_path}.")
        self._last_change = except_exec(file_modified_date, self._file_path)
        self._module = self._import_module(self._file_path)

        for f_name in get_args(FuncName):
            self._patch_function_if_missing(f_name)

    @staticmethod
    def _import_module(file_path: PurePath) -> ModuleType:
        logger.debug(f"Importing module.")
        spec = spec_from_file_location("module.name", file_path)
        module = module_from_spec(spec)
        except_exec(spec.loader.exec_module, module)
        return module

    def _patch_function_if_missing(self, f_name: FuncName):
        if not hasattr(self._module, f_name):
            if f_name == "postprocess":
                setattr(self._module, f_name, dummy_identity)
            else:
                setattr(self._module, f_name, dummy_noop)

            logger.warning(f"Function {f_name} not found.")

    def _save_function_source(self, f_name: FuncName):
        source = except_exec(inspect.getsource, getattr(self._module, f_name))
        self._functions_source_last_exec[f_name] = source

    def _function_has_changed(self, f_name: FuncName):
        source = except_exec(inspect.getsource, getattr(self._module, f_name))
        return self._functions_source_last_exec[f_name] != source

    def _exec_function_and_save_source(self, f_name: FuncName, *args, **kwargs):
        logger.debug(f"Executing function {f_name} and saving source.")
        self._save_function_source(f_name)
        return except_exec(getattr(self._module, f_name), *args, **kwargs)

    def file_has_changed(self):
        return self._last_change != except_exec(file_modified_date, self._file_path)

    def load_data_has_changed(self):
        return self._function_has_changed("load_data")

    def load_data(self):
        return self._exec_function_and_save_source("load_data")

    def make_figure_has_changed(self):
        return self._function_has_changed("make_figure")

    def make_figure(self, fig, data):
        return self._exec_function_and_save_source("make_figure", fig, data)

    def settings_has_changed(self):
        return self._function_has_changed("settings")

    def settings(self, plt_instance):
        return self._exec_function_and_save_source("settings", plt_instance)


class PlotWatcher:
    def __init__(self, file_path: PurePath):
        logger.debug(f"Creating PlotWatcher for {file_path}.")
        self.file_path: PurePath = file_path
        self.wrapped_fig: WrappedFig = WrappedFig()
        self.plotting_code: PlottingCode = PlottingCode(self.file_path)
        self.interactive_elements = None
        self.data = None

    def setup(self):
        logger.debug(f"PlotWatcher: Setup.")
        self.plotting_code.load_module()
        self._initial_plot()

    def _initial_plot(self):
        logger.debug(f"PlotWatcher: Creating initial plot.")
        self.data = self.plotting_code.load_data()
        self.plotting_code.settings(plt)
        self.wrapped_fig.close_without_exit()
        self.wrapped_fig.new_figure()
        self.wrapped_fig.fig.clear()
        self.interactive_elements = self.plotting_code.make_figure(
            self.wrapped_fig.fig, self.data
        )
        plt.draw()

    def _refresh(self):
        if self.plotting_code.file_has_changed():
            logger.debug(f"PlotWatcher: Refresh: plotting code has changed.")
            self.plotting_code.load_module()

            needs_redraw = False
            if self.plotting_code.load_data_has_changed():
                logger.debug(f"PlotWatcher: load_data has changed.")
                self.data = self.plotting_code.load_data()
                needs_redraw = True
                logger.info("Reloaded load_data")

            if self.plotting_code.settings_has_changed():
                logger.debug(f"PlotWatcher: settings has changed.")
                self.plotting_code.settings(plt)
                self.wrapped_fig.close_without_exit()
                self.wrapped_fig.new_figure()
                needs_redraw = True
                logger.info("Reloaded settings")

            if needs_redraw or self.plotting_code.make_figure_has_changed():
                logger.debug(f"PlotWatcher: needs to redraw.")
                self.wrapped_fig.fig.clear()
                self.interactive_elements = self.plotting_code.make_figure(
                    self.wrapped_fig.fig, self.data
                )
                plt.draw()
                logger.info("Reloaded make_figure")

    def refresh_loop(self):
        while True:
            self._refresh()
            plt.pause(1)
