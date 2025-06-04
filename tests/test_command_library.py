import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utilities.command_library import scanner_command


def test_parse_response_ok():
    cmd = scanner_command('TEST')
    assert cmd.parse_response('OK') == 'OK'


def test_parse_response_error():
    cmd = scanner_command('TEST')
    with pytest.raises(Exception):
        cmd.parse_response('ERR')


def test_parse_response_err_substring():
    cmd = scanner_command('TEST')
    # Ensure substring 'ERR' within a valid response does not raise
    assert cmd.parse_response('CARRIER') == 'CARRIER'
