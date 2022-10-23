import os
import string
import tempfile
import time
from collections import namedtuple
from pathlib import Path
from random import choices
from typing import Optional
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session")
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


MockStat = namedtuple("MockStat", "st_mtime st_mode")


mocked_stat_increment = 0


@pytest.fixture(scope="session")
def mock_stat():
    def _mock_stat(filepath):
        global mocked_stat_increment
        mocked_stat_increment += 1
        return MockStat(
            st_mtime=filepath.stat().st_mtime + mocked_stat_increment,
            st_mode=filepath.stat().st_mode,
        )

    return _mock_stat


@pytest.fixture(scope="session")
def make_module(tmp_dir):  # pylint: disable=redefined-outer-name
    def _make_module(module_code, filepath: Optional[Path] = None) -> Path:
        """Write the module code to a file and return the Path.

        The filename is random if not specified.

        The Path object has a stat().st_mtime in the past.
        The :class:`~module_loader` checks it to decide whether to reload.
        We don't want to have to time.sleep(1) between calls.
        """
        if filepath is None:
            filename = "".join(choices(string.ascii_uppercase, k=10)) + ".py"
            filepath = Path(os.path.join(tmp_dir, filename))

        with open(filepath, "w", encoding="utf8") as file_handler:
            file_handler.write(module_code)

        return filepath

    return _make_module
