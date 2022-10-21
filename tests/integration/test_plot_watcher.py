import inspect
import textwrap
from pathlib import Path
from unittest.mock import Mock

from liveplot.__main__ import configure_logs
from liveplot.module_loader import ModuleLoader
from liveplot.plot_watcher import PlotWatcher
from liveplot.plt_interface import PltInterface


def test_loading(make_module):
    filepath = make_module(
        textwrap.dedent(
            """
            """
        )
    )

    watcher = PlotWatcher.from_filepath(Path(filepath), PltInterface(show=False))
    watcher.refresh()

    assert watcher.plt_module.call("load_data") is None
    assert watcher.plt_module.call("postprocess", None) is None
    assert watcher.plt_module.call("settings", None) is None
    assert watcher.plt_module.call("make_figure", None, None) is None


def test_syntax_error_after_first_load_no_crash(make_module):
    filepath = make_module(
        textwrap.dedent(
            """
            """
        )
    )
    mock_plt_i = Mock()

    configure_logs(debug=True)

    watcher = PlotWatcher.from_filepath(filepath, mock_plt_i)
    watcher.refresh()

    make_module(
        textwrap.dedent(
            """
            def load_data():
                return 1
            """
        ),
        filepath=filepath,
    )
    watcher.refresh()

    print(inspect.getsource(watcher.plt_module._module.load_data))

    assert watcher.data == 1
