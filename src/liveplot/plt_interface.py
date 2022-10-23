"""Wrapper for calls to pyplot.

Only used by :class:`~PlotWatcher`, but kept as a separate class so it can be
replaced by a dummy class during tests to check the logic without plotting.
"""
import sys
from typing import Callable, Optional

from matplotlib import pyplot as plt


class PltInterface:
    """Utility functions that have to do with pyplt."""

    def __init__(self):
        self.fig = None
        self._close_handler = None
        self.plt = plt

    def new_figure(self):
        """Create a new figure that exits the program when closed."""
        if self.fig is not None:
            self.fig.canvas.mpl_disconnect(self._close_handler)
            plt.close(self.fig)

        self.fig = plt.figure()
        self._close_handler: Optional[Callable] = self.fig.canvas.mpl_connect(
            "close_event", lambda event: sys.exit()
        )
        self.plt.show(block=False)

    def clear(self):
        self.fig.clear()

    def draw(self):
        self.plt.draw()

    def pause(self, interval: int):
        self.plt.pause(interval)
