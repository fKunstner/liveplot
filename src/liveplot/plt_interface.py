import sys
from typing import Callable, Optional

from matplotlib import pyplot as plt


class PltInterface:
    """Utility functions that have to do with pyplt."""

    def __init__(self, show=True):
        self.fig = None
        self._close_handler = None
        self.plt = plt
        self.show = show

    def new_figure(self):
        """Create a new figure that exits the program when closed."""
        if self.fig is not None:
            self.fig.canvas.mpl_disconnect(self._close_handler)
            plt.close(self.fig)

        self.fig = plt.figure()
        self._close_handler: Optional[Callable] = self.fig.canvas.mpl_connect(
            "close_event", lambda event: sys.exit()
        )
        self.show_or_save()

    def clear(self):
        self.fig.clear()

    def draw(self):
        self.plt.draw()

    def pause(self, interval: int):
        self.plt.pause(interval)

    def show_or_save(self):
        if self.show:
            self.plt.show(block=False)
