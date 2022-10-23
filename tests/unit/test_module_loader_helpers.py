import textwrap
from pathlib import Path

import pytest

# noinspection PyProtectedMember
from liveplot.module_loader import _import_module

# pylint: disable=missing-docstring


def test_import_empty_module(make_module):
    _import_module(make_module(""))


def test_import_invalid_path():
    with pytest.raises(FileNotFoundError):
        _import_module(Path(""))


def test_import_syntax_error(make_module):
    with pytest.raises(ImportError):
        _import_module(make_module("def f() return 1"))


def test_import_module_with_function(make_module):
    module = _import_module(make_module("def f(): return 1"))
    assert module.f() == 1


def test_import_module_that_imports_dependencies(make_module):
    module = _import_module(
        make_module(
            textwrap.dedent(
                """\
                import matplotlib
                import numpy as np
                """
            ),
        )
    )
    assert hasattr(module, "matplotlib")
    assert hasattr(module, "np")
