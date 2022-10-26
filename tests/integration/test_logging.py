import logging

import pytest

from liveplot.cli import configure_logs


def test_logs_has_no_handlers_by_default(caplog):
    assert logging.getLogger().hasHandlers()


def test_logs_has_handlers_after_configure(caplog):
    configure_logs(debug=False)
    assert logging.getLogger().hasHandlers()


def test_can_log_info_in_default_mode(caplog):
    configure_logs(debug=False)
    logging.getLogger("liveplot").info("some info")
    assert "some info" in caplog.text


def test_cannot_log_debug_in_default_mode(caplog):
    configure_logs(debug=False)
    logging.getLogger("liveplot").debug("some info")
    assert "some info" not in caplog.text


def test_can_log_debug_in_debug_mode(caplog):
    configure_logs(debug=True)
    logging.getLogger("liveplot").debug("some info")
    assert "some info" in caplog.text
