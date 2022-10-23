import logging
from pathlib import Path
from typing import Optional

from liveplot.module_loader import ModuleLoader, PlottingModuleError
from liveplot.plt_interface import PltInterface

logger = logging.getLogger("liveplot.plot_watcher")


class PlotWatcher:
    def __init__(self, plotting_module: ModuleLoader, plotting_stuff: PltInterface):
        self.plt_module = plotting_module
        self.plt_interface = plotting_stuff
        self.data = None
        self.interactive_elements = None

    @staticmethod
    def from_path(file_path: Path, plt_interface: Optional[PltInterface] = None):
        logger.debug(f"Creating PlotWatcher for {file_path}")

        return PlotWatcher(
            ModuleLoader(file_path),
            plt_interface if plt_interface is not None else PltInterface(show=True),
        )

    def _make_plot(self):
        has_changed = self.plt_module.func_has_changed
        should_settings = has_changed("settings")
        should_load_data = has_changed("load_data")
        should_postprocess = should_load_data or has_changed("postprocess")
        should_make_figure = (
            should_postprocess or should_settings or has_changed("make_figure")
        )

        if should_load_data:
            logger.debug("PlotWatcher: load_data has changed")
            self.data = self.plt_module.call("load_data")
            logger.info("Reloaded load_data")

        if should_postprocess:
            logger.debug("PlotWatcher: postprocess has changed")
            self.data = self.plt_module.call("postprocess", self.data)
            logger.info("Reloaded postprocess")

        if should_settings:
            logger.debug("PlotWatcher: settings has changed")
            self.plt_module.call("settings", self.plt_interface.plt)
            self.plt_interface.new_figure()
            logger.info("Reloaded settings")

        if should_make_figure:
            logger.debug("PlotWatcher: needs to redraw")
            self.plt_interface.clear()
            self.interactive_elements = self.plt_module.call(
                "make_figure", self.plt_interface.fig, self.data
            )
            self.plt_interface.draw()
            logger.info("Reloaded make_figure")

    def refresh(self):
        if self.plt_module.should_reload():
            logger.debug("PlotWatcher: Refresh: plotting code has changed")

            try:
                self.plt_module.load_module()
            except ImportError as exc:
                logger.error(exc.msg)
                logger.exception(exc.__cause__, exc_info=exc.__cause__)
                return

            try:
                self._make_plot()
            except PlottingModuleError as exc:
                logger.error(str(exc))
                logger.exception(exc.__cause__, exc_info=exc.__cause__)
                return
