import logging
import sys
from pathlib import Path
from typing import Callable, Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from liveplot.module_loader import ModuleLoader, _except_exec

logger = logging.getLogger("liveplot")


class PlotWatcher:
    def __init__(self, file_path: Path):
        logger.debug(f"Creating PlotWatcher for {file_path}.")

        self.file_path: Path = file_path
        self.plotting_code: ModuleLoader = ModuleLoader(
            self.file_path,
            patch_if_missing={
                "load_data": lambda: None,
                "postprocess": lambda data: data,
                "make_figure": lambda fig, data: None,
                "settings": lambda plt_instance: None,
            },
        )

        self.data = None
        self.fig: Optional[Figure] = None
        self.interactive_elements = None
        self._close_handler: Optional[Callable] = None

    def setup(self):
        logger.debug("PlotWatcher: Setup.")
        self.plotting_code.load_module()
        self._initial_plot()

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

    def _initial_plot(self):
        logger.debug("PlotWatcher: Creating initial plot.")
        self.data = self.plotting_code.call("load_data")
        self.data = self.plotting_code.call("postprocess", self.data)

        self.plotting_code.call("settings", plt)
        self.new_figure()
        self.fig.clear()

        self.interactive_elements = self.plotting_code.call(
            "make_figure", self.fig, self.data
        )
        plt.draw()

    def _refresh(self):
        if self.plotting_code.file_has_changed():
            logger.debug("PlotWatcher: Refresh: plotting code has changed.")
            _except_exec(self.plotting_code.load_module)

            needs_redraw = False
            needs_postprocess = False
            if self.plotting_code.func_has_changed("load_data"):
                logger.debug("PlotWatcher: load_data has changed.")
                self.data = self.plotting_code.call("load_data")
                needs_redraw = True
                needs_postprocess = True
                logger.info("Reloaded load_data")

            if needs_postprocess or self.plotting_code.func_has_changed("postprocess"):
                logger.debug("PlotWatcher: postprocess has changed.")
                self.data = self.plotting_code.call("postprocess", self.data)
                needs_redraw = True
                logger.info("Reloaded postprocess")

            if self.plotting_code.func_has_changed("settings"):
                logger.debug("PlotWatcher: settings has changed.")
                self.plotting_code.call("settings", plt)
                self.close_without_exit()
                self.new_figure()
                needs_redraw = True
                logger.info("Reloaded settings")

            if needs_redraw or self.plotting_code.func_has_changed("make_figure"):
                logger.debug("PlotWatcher: needs to redraw.")
                self.fig.clear()
                self.interactive_elements = self.plotting_code.call(
                    "make_figure", self.fig, self.data
                )
                plt.draw()
                logger.info("Reloaded make_figure")

    def refresh_loop(self):
        while True:
            self._refresh()
            plt.pause(2)
