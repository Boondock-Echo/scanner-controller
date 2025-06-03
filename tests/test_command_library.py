import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utilities.command_library import scanner_command


def test_parse_response_ok():
    cmd = scanner_command('TEST')
    assert cmd.parseResponse('OK') == 'OK'


def test_parse_response_error():
    cmd = scanner_command('TEST')
    with pytest.raises(Exception):
        cmd.parseResponse('ERR')
