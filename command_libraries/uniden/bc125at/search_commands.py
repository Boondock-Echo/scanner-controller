"""
Search functionality commands for the BC125AT.

These commands control the scanner's search features including service search,
custom search, search settings, and frequency lockout functions.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

SEARCH_COMMANDS = {
    # SCO command removed - already in close_call_commands.py
    "GLF": scanner_command(
        name="GLF",
        requires_prg=True,
        set_format="GLF,{ignored}",  # Parameter is ignored for retrieval
        validator=validate_param_constraints(
            [(str, lambda x: True)]  # Any string is acceptable as it's ignored
        ),
        help="""Get Global Lockout Frequencies.

        Format:
        GLF - Get first locked out frequency
        GLF,[IGNORED] - Get next locked out frequency

        Response:
        GLF,[FRQ] - Returns a locked out frequency
        GLF,-1 - No more locked out frequencies

        Notes:
        - Returns frequencies that are globally locked out
        - Call repeatedly to retrieve all locked out frequencies
        - Returns "-1" when no more locked out frequencies exist
        - This command is only acceptable in Programming Mode

        Examples:
        GLF - Get first locked out frequency
        GLF,* - Get next locked out frequency (parameter is ignored)
        """,
    ),
    "ULF": scanner_command(
        name="ULF",
        requires_prg=True,
        set_format="ULF,{frequency}",
        validator=validate_param_constraints(
            [(int, lambda x: 25000 <= x <= 512000)]  # frequency (kHz)
        ),
        help="""Unlock Global Lockout Frequency.

        Format:
        ULF,[FRQ] - Unlock a frequency

        Parameters:
        FRQ : Frequency to unlock (25000-512000 kHz)

        Response:
        ULF,OK - Frequency successfully unlocked

        Examples:
        ULF,155625 - Unlock 155.625 MHz

        Notes:
        - Removes the specified frequency from the global lockout list
        - This command is only acceptable in Programming Mode
        """,
    ),
    "LOF": scanner_command(
        name="LOF",
        requires_prg=True,
        set_format="LOF,{frequency}",
        validator=validate_param_constraints(
            [(int, lambda x: 25000 <= x <= 512000)]  # frequency (kHz)
        ),
        help="""Lock Out Frequency.

        Format:
        LOF,[FRQ] - Lock out a frequency

        Parameters:
        FRQ : Frequency to lock out (25000-512000 kHz)

        Response:
        LOF,OK - Frequency successfully locked out

        Examples:
        LOF,155625 - Lock out 155.625 MHz

        Notes:
        - Adds the specified frequency to the global lockout list
        - Locked out frequencies are skipped during searches
        - This command is only acceptable in Programming Mode
        """,
    ),
    # SSG command removed - already in system_commands.py
    "CSG": scanner_command(
        name="CSG",
        requires_prg=True,
        set_format="CSG,{status_mask}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    lambda x: len(x) == 10 and all(c in "01" for c in x),
                )  # 10-digit binary mask
            ]
        ),
        help="""Get/Set Custom Search Group.

        Format:
        CSG - Get current custom search status
        CSG,[STATUS_MASK] - Set custom search status

        Parameters:
        STATUS_MASK : 10-digit binary mask where each digit is 0 or 1
                     0 = Valid (enabled), 1 = Invalid (disabled)
                     The order matches custom search ranges 1-9,0
                     (where 0 is range 10)

        Examples:
        CSG,0000000000 - Enable all custom search ranges
        CSG,1000000000 - Disable custom search range 1, enable all others

        Notes:
        - Cannot set all custom search ranges to invalid ("1111111111")
        - This command is only acceptable in Programming Mode
        """,
    ),
    "CSP": scanner_command(
        name="CSP",
        requires_prg=True,
        set_format="CSP,{index},{lower_limit},{upper_limit}",
        validator=validate_param_constraints(
            [
                (int, lambda x: 1 <= x <= 10),  # index (1-10)
                (int, lambda x: 25000 <= x <= 512000),  # lower_limit (kHz)
                (int, lambda x: 25000 <= x <= 512000),  # upper_limit (kHz)
            ]
        ),
        help="""Get/Set Custom Search Settings.

        Format:
        CSP,[INDEX] - Get custom search settings
        CSP,[INDEX],[LIMIT_L],[LIMIT_H] - Set custom search settings

        Parameters:
        INDEX : Custom search range index (1-10)
        LIMIT_L : Lower limit frequency in kHz (25000-512000)
        LIMIT_H : Upper limit frequency in kHz (25000-512000)

        Examples:
        CSP,1 - Get settings for custom search range 1
        CSP,1,450000,470000 - Set custom search range 1 to 450.000-470.000 MHz

        Notes:
        - In set command, only filled parameters are changed
        - This command is only acceptable in Programming Mode
        """,
    ),
    # WXS command removed - already in weather_commands.py

    # Placeholders for missing commands
    # "JNT": scanner_command(
    #     name="JNT",
    #     requires_prg=False,
    #     set_format="JNT,{frequency}",
    #     validator=validate_param_constraints([]),
    #     help="""Jump to Next Transmission.
    #
    #     Format:
    #     JNT - Jump to next transmission
    #     JNT,[FREQUENCY] - Jump to frequency
    #     """,
    # ),

    # "QSH": scanner_command(
    #     name="QSH",
    #     requires_prg=False,
    #     set_format="QSH,{frequency}",
    #     validator=validate_param_constraints([]),
    #     help="""Quick Search.
    #
    #     Format:
    #     QSH - Start quick search
    #     QSH,[FREQUENCY] - Quick search at frequency
    #     """,
    # ),
}

# Set source module for each command
for cmd in SEARCH_COMMANDS.values():
    cmd.source_module = "SEARCH_COMMANDS"
