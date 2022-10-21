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

    assert not loader.file_has_changed()

    make_module("def f(x): return x+x", filepath=filepath)

    assert loader.file_has_changed()


def test_can_detect_function_change(make_module):
    filepath = make_module("")

    loader = ModuleLoader(filepath, patch_if_missing={"f": lambda x: x})
    loader.load_module()

    assert loader.call("f", 1) == 1

    make_module("def f(x): return x+x", filepath=filepath)
    loader.load_module()

    assert loader.func_has_changed("f")


def test_errors_if_ask_for_change_on_never_exec_func(make_module):
    filepath = make_module("")

    loader = ModuleLoader(filepath, patch_if_missing={"f": lambda x: x})
    loader.load_module()

    make_module("def f(x): return x+x", filepath=filepath)
    loader.load_module()

    with pytest.raises(ValueError):
        loader.func_has_changed("f")
