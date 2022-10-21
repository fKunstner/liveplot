import time

import pytest

from liveplot.module_loader import ModuleLoader


def test_import_empty(make_module):
    loader = ModuleLoader(make_module(""))
    loader.load_module()


def test_patch_if_missing(make_module):
    loader = ModuleLoader(make_module(""), patch_if_missing={"f": lambda x: x})
    loader.load_module()
    assert loader.call("f", 1) == 1


def test_override_patch_if_edit(make_module):
    filepath = make_module("")

    loader = ModuleLoader(filepath, patch_if_missing={"f": lambda x: x})
    loader.load_module()

    assert loader.call("f", 1) == 1

    make_module("def f(x): return x+x", filepath=filepath)
    loader.load_module()

    assert loader.call("f", 1) == 2


def test_can_detect_file_change(make_module):
    filepath = make_module("")

    loader = ModuleLoader(filepath, patch_if_missing={"f": lambda x: x})
    loader.load_module()

    assert not loader.should_reload()

    # Sleep before edit to make sure we don't end up saving at the same timestamp,
    # leading to the change not being detected.
    time.sleep(0.1)
    make_module("def f(x): return x+x", filepath=filepath)

    assert loader.should_reload()


def test_can_detect_function_change(make_module):
    filepath = make_module("")

    loader = ModuleLoader(filepath, patch_if_missing={"f": lambda x: x})
    loader.load_module()

    assert loader.call("f", 1) == 1

    make_module("def f(x): return x+x", filepath=filepath)
    loader.load_module()

    assert loader.func_has_changed("f")
