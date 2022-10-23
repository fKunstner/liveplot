import textwrap
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from liveplot.__main__ import configure_logs
from liveplot.plot_watcher import PlotWatcher
from liveplot.plt_interface import PltInterface


def test_loading(make_module, mock_stat):
    filepath = make_module(
        textwrap.dedent(
            """
            """
        )
    )

    watcher = PlotWatcher.from_path(filepath, PltInterface(show=False))
    watcher.refresh()

    assert watcher.plt_module.call("load_data") is None
    assert watcher.plt_module.call("postprocess", None) is None
    assert watcher.plt_module.call("settings", None) is None
    assert watcher.plt_module.call("make_figure", None, None) is None


def test_syntax_error_after_first_load_no_crash(make_module, mock_stat):
    empty_module = ""
    filepath = make_module(empty_module)
    mock_plt_i = Mock()

    configure_logs(debug=True)
    watcher = PlotWatcher.from_path(filepath, mock_plt_i)
    watcher.refresh()

    module_with_load = textwrap.dedent(
        """
        def load_data(): return 1
        """
    )
    make_module(module_with_load, filepath=filepath)
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        watcher.refresh()
        assert watcher.data == 1

    module_with_load_process = module_with_load + textwrap.dedent(
        """
        
        def postprocess(data): return data + data
        """
    )
    make_module(module_with_load_process, filepath=filepath)
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        watcher.refresh()
        assert watcher.data == 2

    module_with_load_process_settings = module_with_load_process + textwrap.dedent(
        """
        
        def settings(plt): plt.my_data = 1
        """
    )
    make_module(module_with_load_process_settings, filepath=filepath)
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        watcher.refresh()
        assert watcher.data == 2
        assert watcher.plt_interface.plt.my_data == 1

    module_with_everything = module_with_load_process_settings + textwrap.dedent(
        """
        
        def make_figure(fig, data): fig.my_data = data
        """
    )
    make_module(module_with_everything, filepath=filepath)
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        watcher.refresh()
        assert watcher.data == 2
        assert watcher.plt_interface.plt.my_data == 1
        assert watcher.plt_interface.fig.my_data == 2


def test_logging_invalid_syntax_on_load(make_module, mock_stat, caplog):
    configure_logs()

    filepath = make_module("def f() False")
    watcher = PlotWatcher.from_path(filepath, Mock())
    watcher.refresh()

    assert "invalid syntax" in caplog.text


def test_logging_invalid_syntax_on_reload(make_module, mock_stat, caplog):
    configure_logs()

    filepath = make_module("")
    watcher = PlotWatcher.from_path(filepath, Mock())
    watcher.refresh()

    make_module("def f() None", filepath=filepath)
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        watcher.refresh()

    assert "invalid syntax" in caplog.text


@pytest.mark.parametrize(
    "bad_function",
    ["load_data()", "postprocess(data)", "settings(plt)", "make_figure(fig, data)"],
)
def test_logging_user_plotting_code_error(bad_function, make_module, mock_stat, caplog):
    configure_logs()

    filepath = make_module("")
    watcher = PlotWatcher.from_path(filepath, Mock())
    watcher.refresh()

    make_module(
        textwrap.dedent(
            f"""
            def {bad_function}: 
                a = {{"k": 0}}
                a["not_k"]
            """
        ),
        filepath=filepath,
    )
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        watcher.refresh()

    assert "Plotting triggered an exception" in caplog.text
    assert "not_k" in caplog.text
    assert "KeyError" in caplog.text
