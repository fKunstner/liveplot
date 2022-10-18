import tempfile

import pytest


@pytest.fixture(scope="session")
def tmpfolder():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname
