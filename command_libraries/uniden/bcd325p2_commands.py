"""
Bcd325P2 Commands module.

This module provides functionality related to bcd325p2 commands.
It includes command definitions, help text, and utility functions for
interacting with the BCD325P2 scanner.
"""

# Application imports
from .bcd325p2.basic_commands import BASIC_COMMANDS
from .bcd325p2.channel_group_commands import CHANNEL_GROUP_COMMANDS
from .bcd325p2.close_call_commands import CLOSE_CALL_COMMANDS
from .bcd325p2.freq_management_commands import FREQUENCY_MANAGEMENT_COMMANDS
from .bcd325p2.gps_location_commands import GPS_LOCATION_COMMANDS
from .bcd325p2.programming_commands import PROGRAMMING_CONTROL_COMMANDS
from .bcd325p2.scan_config_commands import SCANNER_CONFIGURATION_COMMANDS
from .bcd325p2.scan_search_commands import SCAN_SEARCH_COMMANDS
from .bcd325p2.specialized_functions import SPECIALIZED_COMMANDS
from .bcd325p2.status_info_commands import STATUS_INFO_COMMANDS
from .bcd325p2.talkgroup_commands import TALKGROUP_COMMANDS
from .bcd325p2.trunking_commands import TRUNKING_COMMANDS
from .bcd325p2.weather_alert_commands import WEATHER_ALERT_COMMANDS

# Aggregate all commands into one dictionary
commands = {}
commands.update(BASIC_COMMANDS)
commands.update(CHANNEL_GROUP_COMMANDS)
commands.update(CLOSE_CALL_COMMANDS)
commands.update(FREQUENCY_MANAGEMENT_COMMANDS)
commands.update(GPS_LOCATION_COMMANDS)
commands.update(PROGRAMMING_CONTROL_COMMANDS)
commands.update(SCANNER_CONFIGURATION_COMMANDS)
commands.update(SCAN_SEARCH_COMMANDS)
commands.update(SPECIALIZED_COMMANDS)
commands.update(STATUS_INFO_COMMANDS)
commands.update(TALKGROUP_COMMANDS)
commands.update(TRUNKING_COMMANDS)
commands.update(WEATHER_ALERT_COMMANDS)


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
