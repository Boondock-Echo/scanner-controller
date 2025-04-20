"""
BCD325P2 commands bridge module.

This module imports commands from the appropriate command libraries
and ensures they're properly categorized for the help system.
"""

# Import commands from command libraries
from command_libraries.uniden.bcd325p2.basic_commands import BASIC_COMMANDS
from command_libraries.uniden.bcd325p2.channel_group_commands import (
    CHANNEL_GROUP_COMMANDS,
)
from command_libraries.uniden.bcd325p2.close_call_commands import (
    CLOSE_CALL_COMMANDS,
)
from command_libraries.uniden.bcd325p2.freq_management_commands import (
    FREQUENCY_MANAGEMENT_COMMANDS,
)
from command_libraries.uniden.bcd325p2.gps_location_commands import (
    GPS_LOCATION_COMMANDS,
)
from command_libraries.uniden.bcd325p2.programming_commands import (
    PROGRAMMING_CONTROL_COMMANDS,
)
from command_libraries.uniden.bcd325p2.scan_config_commands import (
    SCANNER_CONFIGURATION_COMMANDS,
)
from command_libraries.uniden.bcd325p2.scan_search_commands import (
    SCAN_SEARCH_COMMANDS,
)
from command_libraries.uniden.bcd325p2.specialized_functions import (
    SPECIALIZED_COMMANDS,
)
from command_libraries.uniden.bcd325p2.system_commands import (
    SYSTEM_CONFIGURATION_COMMANDS,
)
from command_libraries.uniden.bcd325p2.trunking_commands import (
    TRUNKING_COMMANDS,
)

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
commands.update(SYSTEM_CONFIGURATION_COMMANDS)
commands.update(TRUNKING_COMMANDS)

# Ensure all commands have their source_module set
for module_name, module_dict in {
    "BASIC_COMMANDS": BASIC_COMMANDS,
    "CHANNEL_GROUP_COMMANDS": CHANNEL_GROUP_COMMANDS,
    "CLOSE_CALL_COMMANDS": CLOSE_CALL_COMMANDS,
    "FREQUENCY_MANAGEMENT_COMMANDS": FREQUENCY_MANAGEMENT_COMMANDS,
    "GPS_LOCATION_COMMANDS": GPS_LOCATION_COMMANDS,
    "PROGRAMMING_CONTROL_COMMANDS": PROGRAMMING_CONTROL_COMMANDS,
    "SCANNER_CONFIGURATION_COMMANDS": SCANNER_CONFIGURATION_COMMANDS,
    "SCAN_SEARCH_COMMANDS": SCAN_SEARCH_COMMANDS,
    "SPECIALIZED_COMMANDS": SPECIALIZED_COMMANDS,
    "SYSTEM_CONFIGURATION_COMMANDS": SYSTEM_CONFIGURATION_COMMANDS,
    "TRUNKING_COMMANDS": TRUNKING_COMMANDS,
}.items():
    for cmd in module_dict.values():
        cmd.source_module = module_name
        # Make sure command name exists for lookup
        if not hasattr(cmd, 'name'):
            cmd.name = next(k for k, v in module_dict.items() if v is cmd)


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
