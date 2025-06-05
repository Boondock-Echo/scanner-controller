"""
Extended help topics for scanner commands.

This module provides detailed help and examples for scanner commands.
"""

DETAILED_HELP = {
    "channel": """
Channel Command Usage:
---------------------
The 'channel' command reads channel information from your scanner.

Syntax: channel <channel_number>

Examples:
  channel 1     # Read information for channel 1
  channel 42    # Read information for channel 42

Response format varies by scanner model but typically includes:
- Channel number
- Name
- Frequency
- Modulation
- CTCSS/DCS code
- Delay setting
- Lockout status
- Priority status
""",
    "keys": """
Keys Command Usage:
-----------------
The 'keys' command simulates pressing keys on the scanner's keypad.

Syntax: keys <key_sequence>

Valid keys depend on scanner model but typically include:
0-9     : Numeric keys
E       : Enter/E key
F       : Function/F key
M       : Menu key
H       : Hold key
S       : Scan key
L       : Lockout key
P       : Priority key
<       : Left key
>       : Right key
^       : Up key
.       : Decimal point

Examples:
  keys 123      # Press keys 1, 2, 3 in sequence
  keys MHE      # Press Menu, Hold, Enter in sequence
""",
    "hold": """
Hold Command Usage:
-----------------
The 'hold' command puts the scanner in frequency hold mode.

Syntax: hold <frequency>

The frequency should be specified in MHz.

Examples:
  hold 154.725      # Hold on 154.725 MHz
  hold 460.550      # Hold on 460.550 MHz
""",
    "dump": """
Dump Command Usage:
-----------------
The 'dump' command dumps scanner memory to a file.

Syntax: dump [filename]

If filename is not provided, defaults to "memorydump.txt".

Examples:
  dump            # Dump to memorydump.txt
  dump backup.txt # Dump to backup.txt

Note: This can take several minutes to complete.
""",
    "closecall": """
Close Call Commands:
-------------------
The adapter exposes helper methods to control the Close Call feature.

Methods:
  get_close_call       - return raw CLC settings
  set_close_call       - send new CLC parameters
  jump_mode            - jump to a search or Close Call mode
  jump_to_number_tag   - jump to a system/channel number tag
""",
}


def get_extended_help(topic):
    """Get extended help for a specific topic."""
    return DETAILED_HELP.get(topic.lower(), None)
