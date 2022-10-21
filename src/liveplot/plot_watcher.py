import logging
import traceback
from pathlib import Path
from typing import Optional

from liveplot.module_loader import ModuleExecutionError, ModuleLoader
from liveplot.plt_interface import PltInterface

logger = logging.getLogger("liveplot")


def log_error_message(thing: str, exc: Exception):
    logger.error(thing + " failed. Waiting on next save to reload.")
    if isinstance(exc, ModuleExecutionError):
        actual_exc = exc.__cause__
        tb_lines = traceback.format_exception(
            actual_exc.__class__, actual_exc, actual_exc.__traceback__
        )
        logger.error("".join(tb_lines))


class PlotWatcher:
    """Main logic for watching the plotting code."""

    def __init__(self, plotting_module: ModuleLoader, plotting_stuff: PltInterface):
        self.plt_module = plotting_module
        self.plt_interface = plotting_stuff
        self.data = None
        self.interactive_elements = None

    @staticmethod
    def from_filepath(file_path: Path, plt_interface: Optional[PltInterface] = None):
        """Create a PlotWatcher for a specific file.

        Creates a :class:`~ModuleLoader` with dummy functions for load_data,
        postprocess, settings and make_figure.

        Loads a :class:`~PltInterface` with the default pyplot gui.
        """
        logger.debug(f"Creating PlotWatcher for {file_path}.")

        def dummy_load_data():
            return None

        # noinspection PyUnusedLocal
        def dummy_postprocess(data):
            return data

        # noinspection PyUnusedLocal
        # pylint: disable=unused-argument
        def dummy_make_figure(fig, data):
            return None

        # noinspection PyUnusedLocal
        # pylint: disable=unused-argument
        def dummy_settings(plt):
            return None

        return PlotWatcher(
            ModuleLoader(
                file_path,
                patch_if_missing={
                    "load_data": dummy_load_data,
                    "postprocess": dummy_postprocess,
                    "make_figure": dummy_make_figure,
                    "settings": dummy_settings,
                },
            ),
            plt_interface if plt_interface is not None else PltInterface(show=True),
        )

    def refresh(self):
        """Make the plot.

        Only calls functions when necessary. We don't need to reload and execute
        the module if it hasn't changed. Same for function if their dependencies
        haven't changed.
        """
        if self.plt_module.should_reload():
            logger.debug("PlotWatcher: Refresh: plotting code has changed.")
            try:
                self.plt_module.load_module()
            except ImportError as exc:
                log_error_message("Reloading the module", exc)
                return

            has_changed = self.plt_module.func_has_changed
            should_load_data = has_changed("load_data")
            should_postprocess = should_load_data or has_changed("postprocess")
            should_settings = has_changed("settings")
            should_make_figure = (
                should_load_data
                or should_postprocess
                or should_settings
                or self.plt_module.func_has_changed("make_figure")
            )

            if should_load_data:
                logger.debug("PlotWatcher: load_data has changed.")
                try:
                    self.data = self.plt_module.call("load_data")
                    logger.info("Reloaded load_data")
                except ModuleExecutionError as exc:
                    log_error_message("load_data", exc)
                    return

            if should_postprocess:
                logger.debug("PlotWatcher: postprocess has changed.")
                try:
                    self.data = self.plt_module.call("postprocess", self.data)
                    logger.info("Reloaded postprocess")
                except ModuleExecutionError as exc:
                    log_error_message("postprocess", exc)
                    return

            if should_settings:
                logger.debug("PlotWatcher: settings has changed.")

                try:
                    self.plt_module.call("settings", self.plt_interface.plt)
                    self.plt_interface.close_without_exit()
                    self.plt_interface.new_figure()
                    logger.info("Reloaded settings")
                except ModuleExecutionError as exc:
                    log_error_message("settings", exc)
                    return

            if should_make_figure:
                logger.debug("PlotWatcher: needs to redraw.")
                try:
                    self.plt_interface.clear()
                    self.interactive_elements = self.plt_module.call(
                        "make_figure",
                        self.plt_interface.fig,
                        self.data,
                    )
                    self.plt_interface.draw()
                    logger.info("Reloaded make_figure")
                except ModuleExecutionError as exc:
                    log_error_message("make_figure", exc)
                    return
