"""Mocked test for the flow of operations of the plot watcher."""
from unittest.mock import ANY, Mock, call

from liveplot.plot_watcher import PlotWatcher

# pylint: disable=missing-docstring


def test_loading():
    plt_code = Mock()
    plt_interface = Mock()

    watcher = PlotWatcher(plt_code, plt_interface)
    watcher.refresh()

    plt_code.assert_has_calls([call.load_module()], any_order=True)


def test_one_pass():
    plt_code = Mock()
    plt_interface = Mock()

    watcher = PlotWatcher(plt_code, plt_interface)
    watcher.refresh()

    expected_calls = [
        call.call("load_data"),
        call.call("postprocess", ANY),
        call.call("settings", ANY),
        call.call("make_figure", ANY, ANY),
    ]

    plt_code.assert_has_calls(expected_calls, any_order=False)
