import textwrap
from pathlib import PurePath

import pytest

# noinspection PyProtectedMember
from liveplot.code_loader import _import_module, except_exec

# pylint: disable=missing-docstring


def test_except_exec_doesnt_trigger_exception():
    def raise_exception():
        raise NotImplementedError

    except_exec(raise_exception)


def test_import_empty_module(make_module):
    _import_module(make_module(""))


def test_import_invalid_path():
    with pytest.raises(ImportError):
        _import_module(PurePath(""))


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


def test_import_module_with_syntax_error(make_module):
    with pytest.raises(SyntaxError):
        _import_module(make_module("def f() return"))
