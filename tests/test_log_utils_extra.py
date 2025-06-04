"""Additional tests for :mod:`utilities.log_utils`."""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utilities.log_utils import configure_logging  # noqa: E402


def _clear_root_handlers():
    """Remove all handlers attached to the root logger."""
    root = logging.getLogger("")
    for h in list(root.handlers):
        root.removeHandler(h)


def test_configure_logging_creates_file_and_level(tmp_path):
    """Create a log file at the specified level."""
    _clear_root_handlers()
    log_file = tmp_path / "app.log"
    configure_logging(str(log_file), level=logging.WARNING)
    assert log_file.exists()
    assert logging.getLogger("").level == logging.WARNING


def test_configure_logging_trims_large_file(tmp_path):
    """Ensure large log files are trimmed when configured."""
    log_file = tmp_path / "big.log"
    log_file.write_bytes(b"a" * 2048)
    _clear_root_handlers()
    configure_logging(str(log_file), level=logging.INFO, max_size_mb=0)
    assert os.path.getsize(log_file) < 2048
