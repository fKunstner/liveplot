import os
import pdb
import string
import tempfile
from pathlib import PurePath
from random import choices

import pytest

from liveplot.plot_watcher import _import_module, except_exec


def test_except_exec_doesnt_trigger_exception():
    def raise_exception():
        raise NotImplementedError

    except_exec(raise_exception)


def make_module(tmpfolder, module_code):
    filename = "".join(choices(string.ascii_uppercase, k=10)) + ".py"
    filepath = os.path.join(tmpfolder, filename)
    with open(filepath, "w") as f:
        f.write(module_code)
    return PurePath(filepath)


def test_load_empty(tmpfolder):
    _import_module(make_module(tmpfolder, ""))


def test_load_module(tmpfolder):
    module = _import_module(make_module(tmpfolder, "def f(): return 1"))
    assert module.f() == 1


def test_load_import_mpl(tmpfolder):
    module = _import_module(make_module(tmpfolder, "import matplotlib"))
    assert hasattr(module, "matplotlib")


@pytest.mark.xfail
def test_load_bad_code(tmpfolder):
    _import_module(make_module(tmpfolder, "def f() return"))
