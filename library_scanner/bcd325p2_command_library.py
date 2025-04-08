"""
LEGACY COMMAND LIBRARY - REDIRECTS TO NEW LOCATION
This file is kept for backward compatibility and redirects to command_libraries/uniden/bcd325p2_commands.py
"""

import warnings
warnings.warn(
    "Using library_scanner.bcd325p2_command_library is deprecated. "
    "Please use command_libraries.uniden.bcd325p2_commands instead.",
    DeprecationWarning, 
    stacklevel=2
)

from command_libraries.uniden.bcd325p2_commands import commands, getHelp, listCommands