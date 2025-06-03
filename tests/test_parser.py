"""Unit tests for the :mod:`utilities.command.parser` module."""

import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.command.parser import parse_command


def test_parse_command_aliases_and_multiword():
    commands = {
        "get freq": None,
        "set option": None,
        "scan start": None,
    }

    cmd, args = parse_command("read freq", commands)
    assert cmd == "get freq"
    assert args == ""

    cmd, args = parse_command("write option 1", commands)
    assert cmd == "set option"
    assert args == "1"

    cmd, args = parse_command("scan start now", commands)
    assert cmd == "scan start"
    assert args == "now"


def test_parse_command_unknown():
    commands = {}
    cmd, args = parse_command("foo bar baz", commands)
    assert cmd == "foo"
    assert args == "bar baz"
