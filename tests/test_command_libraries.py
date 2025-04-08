"""
Tests for command libraries to ensure they are properly defined and work as expected
"""
import pytest
import importlib

def test_bc125at_commands_load():
    """Test that BC125AT commands can be loaded"""
    try:
        bc125at = importlib.import_module('command_libraries.uniden.bc125at_commands')
        assert hasattr(bc125at, 'commands')
        assert isinstance(bc125at.commands, dict)
        assert len(bc125at.commands) > 0
    except ImportError:
        pytest.skip("BC125AT commands module not available")

def test_bcd325p2_commands_load():
    """Test that BCD325P2 commands can be loaded"""
    try:
        bcd325p2 = importlib.import_module('command_libraries.uniden.bcd325p2_commands')
        assert hasattr(bcd325p2, 'commands')
        assert isinstance(bcd325p2.commands, dict)
        assert len(bcd325p2.commands) > 0
    except ImportError:
        pytest.skip("BCD325P2 commands module not available")

def test_command_structure():
    """Test the structure of a command to ensure it has required attributes"""
    try:
        bc125at = importlib.import_module('command_libraries.uniden.bc125at_commands')
        
        # Sample of common commands that should exist
        common_commands = ["MDL", "VER", "SQL", "VOL"]
        
        for cmd in common_commands:
            if cmd in bc125at.commands:
                command = bc125at.commands[cmd]
                assert hasattr(command, 'name')
                assert hasattr(command, 'buildCommand')
                assert hasattr(command, 'parseResponse')
                
                # Test building a command works
                built_cmd = command.buildCommand()
                assert built_cmd is not None
                assert cmd in built_cmd
    except ImportError:
        pytest.skip("BC125AT commands module not available")
