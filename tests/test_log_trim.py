"""Tests for :func:`utilities.tools.log_trim.trim_log_file`."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.tools.log_trim import trim_log_file


def test_trim_log_file(tmp_path):
    log = tmp_path / "test.log"
    original = b"a" * 2048
    log.write_bytes(original)

    trim_log_file(str(log), max_size=1024)

    data = log.read_bytes()
    assert len(data) == 1024
    assert data == original[-1024:]


def test_trim_log_file_missing(tmp_path):
    missing = tmp_path / "missing.log"
    trim_log_file(str(missing))
    assert not missing.exists()
