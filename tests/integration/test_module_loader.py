import time
from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from liveplot.module_loader import ModuleLoader


def test_import_empty(make_module):
    loader = ModuleLoader(make_module(""))
    loader.load_module()


def test_patch_if_missing(make_module):
    loader = ModuleLoader(make_module(""))
    loader.load_module()
    assert loader.call("load_data") is None
    assert loader.call("postprocess", 1) == 1
    assert loader.call("settings", None) is None
    assert loader.call("make_figure", None, None) is None


def test_can_detect_file_change(make_module, mock_stat):
    filepath = make_module("")

    loader = ModuleLoader(filepath)
    loader.load_module()

    assert not loader.should_reload()

    make_module("def f(x): return x+x", filepath=filepath)

    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        assert loader.should_reload()


def test_can_detect_function_change(make_module, mock_stat):
    filepath = make_module("")

    loader = ModuleLoader(filepath)
    loader.load_module()

    assert loader.call("postprocess", 1) == 1

    make_module("def postprocess(x): return x+x", filepath=filepath)
    with patch.object(Path, "stat", return_value=mock_stat(filepath)):
        loader.load_module()
        assert loader.func_has_changed("postprocess")
