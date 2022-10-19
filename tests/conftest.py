import os
import string
import tempfile
from pathlib import Path
from random import choices
from typing import Optional

import pytest


@pytest.fixture(scope="session")
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture()
def make_module(tmp_dir):  # pylint: disable=redefined-outer-name
    def _make_module(module_code, filepath: Optional[Path] = None):
        """Writes a module with given filename in directory and returns its path.

        filename is random if not specified.
        """
        if filepath is None:
            filename = "".join(choices(string.ascii_uppercase, k=10)) + ".py"
            filepath = Path(os.path.join(tmp_dir, filename))

        with open(filepath, "w", encoding="utf8") as file_handler:
            file_handler.write(module_code)

        return filepath

    return _make_module
