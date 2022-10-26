import shlex
from pathlib import Path

from liveplot.cli import make_parser


def test_parse_script_filename():
    args = make_parser().parse_args(shlex.split("somefile.py"))
    assert isinstance(args.script, Path)
    assert str(args.script) == "somefile.py"
    assert not args.debug


def test_parse_script_filename_with_debug():
    args = make_parser().parse_args(shlex.split("somefile.py --debug"))
    assert isinstance(args.script, Path)
    assert str(args.script) == "somefile.py"
    assert args.new is False
    assert args.debug is True


def test_new_script_filename():
    args = make_parser().parse_args(shlex.split("--new file.py"))
    assert not args.debug
    assert args.new is True
    assert str(args.script) == "file.py"
