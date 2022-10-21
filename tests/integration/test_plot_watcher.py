import textwrap
import time
from pathlib import Path
from unittest.mock import Mock

from liveplot.__main__ import configure_logs
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


def property_to_check(make_module, modules, to_assert):
    configure_logs(debug=True)
    filepath = make_module("")
    mock_plt_i = Mock()
    watcher = PlotWatcher.from_filepath(filepath, mock_plt_i)

    for module, stmt_to_assert in zip(modules, to_assert):
        time.sleep(0.5)
        make_module(module, filepath=filepath)
        watcher.refresh()
        assert stmt_to_assert


def test_syntax_error_after_first_load_no_crash(make_module):
    property_to_check(
        make_module,
        modules=["", "def load_data() return 1"],
        to_assert=[(lambda _: 1, 1), (lambda _: 1, 1)],
    )


def test_override_dummies(make_module):
    modules = [
        "",
        textwrap.dedent(
            """
            def load_data(): return 1
            """
        ),
        textwrap.dedent(
            """
            def load_data(): return 1
            def postprocess(data): return data + data
            """
        ),
        textwrap.dedent(
            """
            def load_data(): return 1
            def postprocess(data): return data + data
            def settings(plt): plt.my_data = 1
            """
        ),
        textwrap.dedent(
            """
            def load_data(): return 1
            def postprocess(data): return data + data
            def settings(plt): plt.my_data = 1
            def make_figure(fig, data): fig.my_data = data
            """
        ),
    ]

    def assert_initialized(_):
        assert True

    def assert_data(watcher):
        assert watcher.data == 1

    def assert_post(watcher):
        assert watcher.data == 2

    def assert_settings(watcher):
        assert watcher.plt_interface.plt.my_data == 1

    def assert_figure(watcher):
        assert watcher.plt_interface.fig.my_data == 2

    property_to_check(
        make_module,
        modules,
        to_assert=[
            assert_initialized,
            assert_data,
            assert_post,
            assert_settings,
            assert_figure,
        ],
    )


def test_recover_after_syntax_error(make_module):
    property_to_check(
        make_module,
        modules=[
            "",
            textwrap.dedent(
                """
                def load_data(): return 1
                """
            ),
            textwrap.dedent(
                """
                def load_data(): return 1
                def postprocess(data) return data
                """
            ),
            textwrap.dedent(
                """
                def load_data(): return 1
                def postprocess(data): return 2 * data
                """
            ),
        ],
        to_assert=[
            (lambda watcher: watcher.data, 1),
            (lambda watcher: watcher.data, 1),
            (lambda watcher: watcher.data, 2),
        ],
    )


def test_recover_after_error_in_data(make_module):
    empty_module = "def load_data(): return 1"
    filepath = make_module(empty_module)
    mock_plt_i = Mock()

    configure_logs(debug=True)

    watcher = PlotWatcher.from_filepath(filepath, mock_plt_i)
    watcher.refresh()
    assert watcher.data == 1

    module_with_execution_error = textwrap.dedent(
        """
        def load_data():
            a = {"a_key": 2}
            return a["not_a_key"]
        """
    )
    make_module(module_with_execution_error, filepath=filepath)
    watcher.refresh()
    assert watcher.data == 1

    module_without_execution_error = textwrap.dedent(
        """
        def load_data():
            a = {"a_key": 2}
            return a["a_key"]
        """
    )
    make_module(module_without_execution_error, filepath=filepath)
    watcher.refresh()
    assert watcher.data == 2


def test_recover_after_error_in_preprocess(make_module):
    empty_module = "def load_data(): return 1"
    filepath = make_module(empty_module)
    mock_plt_i = Mock()

    configure_logs(debug=True)

    watcher = PlotWatcher.from_filepath(filepath, mock_plt_i)
    watcher.refresh()
    assert watcher.data == 1

    module_with_execution_error = textwrap.dedent(
        """
        def load_data():
            a = {"a_key": 2}
            return a["not_a_key"]
        """
    )
    make_module(module_with_execution_error, filepath=filepath)
    watcher.refresh()
    assert watcher.data == 1

    module_without_execution_error = textwrap.dedent(
        """
        def load_data():
            a = {"a_key": 2}
            return a["a_key"]
        """
    )
    make_module(module_without_execution_error, filepath=filepath)
    watcher.refresh()
    assert watcher.data == 2


def test_recover_after_error_in_settings(make_module):
    empty_module = "def load_data(): return 1"
    filepath = make_module(empty_module)
    mock_plt_i = Mock()

    configure_logs(debug=True)

    watcher = PlotWatcher.from_filepath(filepath, mock_plt_i)
    watcher.refresh()

    module_with_execution_error = textwrap.dedent(
        """
        def settings(plt):
            a = {"key": 1}
            plt.my_setting = a["not_key"]
        """
    )
    make_module(module_with_execution_error, filepath=filepath)
    watcher.refresh()

    module_without_execution_error = textwrap.dedent(
        """
        def settings(plt):
            a = {"key": 1}
            plt.my_setting = a["key"]
        """
    )
    make_module(module_without_execution_error, filepath=filepath)
    watcher.refresh()
    assert watcher.plt_interface.plt.my_setting == 1


def test_recover_after_error_in_make_figure(make_module):
    empty_module = "def load_data(): return 1"
    filepath = make_module(empty_module)
    mock_plt_i = Mock()

    configure_logs(debug=True)

    watcher = PlotWatcher.from_filepath(filepath, mock_plt_i)
    watcher.refresh()

    module_with_execution_error = textwrap.dedent(
        """
        def make_figure(fig, data):
            a = {"key": 1}
            fig.my_setting = a["not_key"]
        """
    )
    make_module(module_with_execution_error, filepath=filepath)
    watcher.refresh()

    module_without_execution_error = textwrap.dedent(
        """
        def make_figure(fig, data):
            a = {"key": 1}
            fig.my_setting = a["key"]
        """
    )
    make_module(module_without_execution_error, filepath=filepath)
    watcher.refresh()
    assert watcher.plt_interface.fig.my_setting == 1
