"""Command definitions for the Uniden BC125AT scanner."""

# Application imports
from .bc125at.basic_commands import BASIC_COMMANDS
from .bc125at.channel_commands import CHANNEL_COMMANDS
from .bc125at.close_call_commands import CLOSE_CALL_COMMANDS
from .bc125at.config_commands import CONFIG_COMMANDS
from .bc125at.programming_commands import PROGRAMMING_COMMANDS
from .bc125at.search_commands import SEARCH_COMMANDS
from .bc125at.status_commands import STATUS_COMMANDS
from .bc125at.system_commands import SYSTEM_COMMANDS
from .bc125at.weather_commands import WEATHER_COMMANDS

# Aggregate all commands into one dictionary
commands = {}
commands.update(BASIC_COMMANDS)
commands.update(CHANNEL_COMMANDS)
commands.update(CLOSE_CALL_COMMANDS)
commands.update(CONFIG_COMMANDS)
commands.update(PROGRAMMING_COMMANDS)
commands.update(SEARCH_COMMANDS)
commands.update(STATUS_COMMANDS)
commands.update(SYSTEM_COMMANDS)
commands.update(WEATHER_COMMANDS)


def get_help(command):
    """
    Return the help string for the specified command (case-insensitive).

    Returns None if command is not defined.
    """
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None


def list_commands():
    """Return a sorted list of all available command names."""
    return sorted(commands.keys())
