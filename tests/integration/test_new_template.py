import os
from pathlib import Path

import pytest

from liveplot.cli import create_template, default_new_template_file


def test_create_template_default_filename(tmp_dir):
    cwd = os.getcwd()
    os.chdir(tmp_dir)
    create_template(None)
    assert Path(default_new_template_file).is_file()
    os.chdir(cwd)


def test_create_template_specified_filename(tmp_dir):
    cwd = os.getcwd()
    os.chdir(tmp_dir)
    create_template(Path("myfile.py"))
    assert Path("myfile.py").is_file()
    os.chdir(cwd)


def test_error_if_file_exists(tmp_dir):
    cwd = os.getcwd()
    os.chdir(tmp_dir)
    create_template(None)
    assert Path(default_new_template_file).is_file()

    with pytest.raises(FileExistsError):
        create_template(None)

    assert Path(default_new_template_file).is_file()
    os.chdir(cwd)
