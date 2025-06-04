"""
Weather alert commands for the BC125AT.

These commands control the weather alert functionality of the scanner,
allowing you to monitor NOAA weather radio broadcasts and receive alerts
during severe weather conditions. The BC125AT can monitor the 7 standard
NOAA weather frequencies (162.400 - 162.550 MHz) and alert you when
warnings are broadcast.
"""

from utilities.core.shared_utils import ScannerCommand
from utilities.validators import validate_param_constraints

WEATHER_COMMANDS = {
    "WXS": ScannerCommand(
        name="WXS",
        requires_prg=True,
        set_format="WXS,{alt_pri}",
        validator=validate_param_constraints(
            [(int, {0, 1})]  # alert priority (0=OFF, 1=ON)
        ),
        help="""Get/Set Weather Alert Settings.

        Format:
        WXS - Get current weather alert settings
        WXS,[ALT_PRI] - Set weather alert priority

        Parameters:
        ALT_PRI : Weather Alert Priority (0=OFF, 1=ON)

        Examples:
        WXS,1 - Enable weather alert priority
        WXS,0 - Disable weather alert priority

        Notes:
        - When enabled, the scanner periodically checks for weather alerts while
            scanning
        - The scanner checks the strongest local NOAA weather channel for alerts
        - Weather alerts can alert you to severe weather conditions in your area
        - NOAA weather radio operates on dedicated frequencies:
          162.400, 162.425, 162.450, 162.475, 162.500, 162.525, and 162.550 MHz
        - This command is only acceptable in Programming Mode
        """,
    )
}

# Set source module for each command
for cmd in WEATHER_COMMANDS.values():
    cmd.source_module = "WEATHER_COMMANDS"
