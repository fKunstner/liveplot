import textwrap
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from liveplot.cli import configure_logs
from liveplot.plot_watcher import PlotWatcher


def test_loading(make_module):
    filepath = make_module(
        textwrap.dedent(
            """
            """
        )
    )

    watcher = PlotWatcher.from_path(filepath, Mock())
    watcher.refresh()

    assert watcher.plt_module.call("load_data") is None
    assert watcher.plt_module.call("postprocess", None) is None
    assert watcher.plt_module.call("settings", None) is None
    assert watcher.plt_module.call("make_figure", None, None) is None


@pytest.mark.parametrize(
    "function_overload_and_check",
    [
        ("def load_data(): return 1", lambda watcher: watcher.data == 1),
        (
            (
                "def load_data(): return 1 \n"
                "def postprocess(data): return data + data"
            ),
            lambda watcher: watcher.data == 2,
        ),
        (
            "def settings(plt): plt.my_data = 1",
            lambda watcher: watcher.plt_interface.plt.my_data == 1,
        ),
        (
            (
                "def load_data(): return 1 \n"
                "def make_figure(fig, data): fig.my_data = data"
            ),
            lambda watcher: watcher.plt_interface.fig.my_data == 1,
        ),
    ],
)
def test_syntax_error_after_first_load_no_crash(
    function_overload_and_check, make_module, mock_stat
):
    configure_logs(debug=True)

    filepath = make_module("")
    watcher = PlotWatcher.from_path(filepath, Mock())
    watcher.refresh()

    function_override, check_func = function_overload_and_check

    make_module(function_override, filepath=filepath)
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        watcher.refresh()
        assert check_func(watcher)


def test_logging_invalid_syntax_on_load(make_module, caplog):
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
