import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from liveplot.module_loader import (
    ModuleExecutionError,
    ModuleLoader,
    wrap_execution_error,
)
from liveplot.plt_interface import PltInterface

logger = logging.getLogger("liveplot.plot_watcher")


def error_thing_failed(thing: str):
    return f"{thing} failed. Waiting on next save to try to reload."


class PlotWatcher:
    def __init__(self, plotting_module: ModuleLoader, plotting_stuff: PltInterface):
        self.plt_module = plotting_module
        self.plt_interface = plotting_stuff
        self.data = None
        self.interactive_elements = None

    @staticmethod
    def from_filepath(file_path: Path, plt_interface: Optional[PltInterface] = None):
        logger.debug(f"Creating PlotWatcher for {file_path}.")

        def dummy_load_data():
            return None

        # noinspection PyUnusedLocal
        def dummy_postprocess(data):
            return data

        # noinspection PyUnusedLocal
        def dummy_make_figure(fig, data):
            return None

        # noinspection PyUnusedLocal
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
        if self.plt_module.should_reload():
            logger.debug("PlotWatcher: Refresh: plotting code has changed.")
            try:
                self.plt_module.load_module()
            except ImportError:
                logger.exception(error_thing_failed("Reloading the module"))
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
                    self.data = wrap_execution_error(self.plt_module.call, "load_data")
                    logger.info("Reloaded load_data")
                except ModuleExecutionError:
                    logger.exception(error_thing_failed("load_data"))
                    return

            if should_postprocess:
                logger.debug("PlotWatcher: postprocess has changed.")
                try:
                    self.data = wrap_execution_error(
                        self.plt_module.call, "postprocess", self.data
                    )
                    logger.info("Reloaded postprocess")
                except ModuleExecutionError:
                    logger.exception(error_thing_failed("postprocess"))
                    return

            if should_settings:
                logger.debug("PlotWatcher: settings has changed.")

                try:
                    wrap_execution_error(
                        self.plt_module.call, "settings", self.plt_interface.plt
                    )
                    self.plt_interface.close_without_exit()
                    self.plt_interface.new_figure()
                    logger.info("Reloaded settings")
                except ModuleExecutionError:
                    logger.exception(error_thing_failed("settings"))
                    return

            if should_make_figure:
                logger.debug("PlotWatcher: needs to redraw.")
                try:
                    self.plt_interface.clear()
                    self.interactive_elements = wrap_execution_error(
                        self.plt_module.call,
                        "make_figure",
                        self.plt_interface.fig,
                        self.data,
                    )
                    self.plt_interface.draw()
                    logger.info("Reloaded make_figure")
                except ModuleExecutionError:
                    logger.exception(error_thing_failed("make_figure"))
                    return
