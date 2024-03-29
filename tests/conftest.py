import itertools
import os
import string
import tempfile
from collections import namedtuple
from pathlib import Path
from random import choices
from typing import Optional

import pytest


@pytest.fixture(scope="session")
def session_tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture(scope="function")
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture(scope="function")
def mock_stat():
    MockStat = namedtuple("MockStat", "st_mtime st_mode")
    counter = itertools.count(start=1, step=1)

    def _mock_stat(filepath):
        return MockStat(
            st_mtime=filepath.stat().st_mtime + next(counter),
            st_mode=filepath.stat().st_mode,
        )

    return _mock_stat


@pytest.fixture(scope="session")
def make_module(session_tmp_dir):  # pylint: disable=redefined-outer-name
    def _make_module(module_code, filepath: Optional[Path] = None) -> Path:
        """Write the module code to a file and return the Path.

        The filename is random if not specified.

        The Path object has a stat().st_mtime in the past.
        The :class:`~module_loader` checks it to decide whether to reload.
        We don't want to have to time.sleep(1) between calls.
        """
        if filepath is None:
            filename = "".join(choices(string.ascii_uppercase, k=10)) + ".py"
            filepath = Path(os.path.join(session_tmp_dir, filename))

        with open(filepath, "w", encoding="utf8") as file_handler:
            file_handler.write(module_code)

        return filepath

    return _make_module
