# BC125AT command definitions for Uniden scanners

"""
Bc125At Commands module.

This module provides functionality related to bc125at commands.
It includes command definitions, help text, and utility functions for
interacting with the BC125AT scanner.
"""

# Application imports
from .bc125at.basic_commands import BASIC_COMMANDS
from .bc125at.channel_commands import CHANNEL_COMMANDS
from .bc125at.close_call_commands import CLOSE_CALL_COMMANDS
from .bc125at.config_commands import CONFIG_COMMANDS
from .bc125at.programming_commands import PROGRAMMING_COMMANDS
from .bc125at.search_commands import SEARCH_COMMANDS
from .bc125at.weather_commands import WEATHER_COMMANDS

# Aggregate all commands into one dictionary
commands = {}
commands.update(BASIC_COMMANDS)
commands.update(CHANNEL_COMMANDS)
commands.update(CLOSE_CALL_COMMANDS)
commands.update(CONFIG_COMMANDS)
commands.update(PROGRAMMING_COMMANDS)
commands.update(SEARCH_COMMANDS)
commands.update(WEATHER_COMMANDS)


def getHelp(command):
    """
    Return the help string for the specified command (case-insensitive).

    Returns None if command is not defined.
    """
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None


def listCommands():
    """Return a sorted list of all available command names."""
    return sorted(commands.keys())
