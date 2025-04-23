"""
Channel Management commands for the BC125AT.

These commands allow you to create, modify, and delete memory channels,
configure channel groups, and control lockout settings. The BC125AT can store
up to 500 conventional channels across 10 banks.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

CHANNEL_COMMANDS = {
    "CIN": scanner_command(
        name="CIN",
        requires_prg=True,
        set_format=(
            "CIN,{index},{name},{freq},{mod},{ctcss_dcs},{delay},{lockout},"
            "{priority}"
        ),
        validator=validate_param_constraints(
            [
                (int, (1, 500)),  # index (1-500)
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (
                    int,
                    lambda x: 25000 <= x <= 512000,
                ),  # frequency (kHz) - BC125AT range
                (str, {"AUTO", "AM", "FM", "NFM"}),  # modulation
                (int, (0, 231)),  # CTCSS/DCS code (0-231)
                (int, {-10, -5, 0, 1, 2, 3, 4, 5}),  # delay time
                (int, {0, 1}),  # lockout (0=Unlocked, 1=Lockout)
                (int, {0, 1}),  # priority (0=OFF, 1=ON)
            ]
        ),
        help="""Get/Set Channel Information.

        Format:
        Get channel information
        CIN,[INDEX]

        Set channel information
        CIN,[INDEX],[NAME],[FRQ],[MOD],[CTCSS/DCS],[DLY],[LOUT],[PRI]

        Parameters:
        INDEX : Channel Index (1-500)
        NAME : Name (max 16 characters)
        FRQ : Channel Frequency in kHz (25000-512000)
        MOD : Modulation (AUTO, AM, FM, NFM)
        CTCSS/DCS : CTCSS/DCS Status (0-231, see code list in manual)
                    0 = None,
                    127 = Search
                    64-113 = CTCSS tones
                    128-231 = DCS codes
        DLY : Delay Time (-10, -5, 0, 1, 2, 3, 4, 5)
        LOUT : Lockout (0=Unlocked, 1=Lockout)
        PRI : Priority (0=OFF, 1=ON)

        Examples:
        CIN,42 - Get information for channel 42
        CIN,42,Police Dispatch,155625,NFM,0,2,0,1 - Set channel 42

        Notes:
        - This command is only acceptable in Programming Mode
        - In set command, only filled parameters are changed
        - The set command is aborted if any format error is detected
        """,
    ),
    "DCH": scanner_command(
        name="DCH",
        requires_prg=True,
        set_format="DCH,{index}",
        validator=validate_param_constraints(
            [(int, (1, 500))]  # channel index (1-500)
        ),
        help="""Delete Channel.

        Format:
        DCH,[INDEX] - Delete a channel

        Parameters:
        INDEX : Channel Index (1-500)

        Examples:
        DCH,42 - Delete channel 42

        Notes:
        - This command deletes the channel at the specified index
        - The scanner must be in Programming Mode to use this command
        - The deleted channel information cannot be recovered
        """,
    ),
    "SCG": scanner_command(
        name="SCG",
        requires_prg=True,
        set_format="SCG,{status_mask}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    lambda x: len(x) == 10 and all(c in "01" for c in x),
                )  # 10-digit binary mask
            ]
        ),
        help="""Get/Set Channel Storage Bank Status.

        Format:
        SCG - Get current bank status
        SCG,[STATUS_MASK] - Set bank status

        Parameters:
        STATUS_MASK : 10-digit binary mask where each digit is 0 or 1
                     0 = Valid (enabled), 1 = Invalid (disabled)
                     The order matches scanner banks 1-9,0 (where 0 is bank 10)

        Examples:
        SCG,0000000000 - Enable all banks
        SCG,1000000000 - Disable bank 1, enable all others
        SCG,0000000001 - Disable bank 10, enable all others

        Notes:
        - Controls which channel storage banks are enabled/disabled
        - Cannot set all banks to disabled ("1111111111")
        - This command is only acceptable in Programming Mode
        """,
    ),
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
    "LOF": scanner_command(
        name="LOF",
        requires_prg=True,
        set_format="LOF,{frequency}",
        validator=validate_param_constraints(
            [(int, lambda x: 25000 <= x <= 512000)]  # frequency in kHz
        ),
        help="""Lock Out Frequency.

        Format:
        LOF,[FRQ] - Lock out a frequency

        Parameters:
        FRQ : Frequency to lock out (25000-512000 kHz)

        Examples:
        LOF,155625 - Lock out 155.625 MHz

        Notes:
        - Adds the specified frequency to the global lockout list
        - Locked out frequencies are skipped during searches
        - This command is only acceptable in Programming Mode
        """,
    ),
    "ULF": scanner_command(
        name="ULF",
        requires_prg=True,
        set_format="ULF,{frequency}",
        validator=validate_param_constraints(
            [(int, lambda x: 25000 <= x <= 512000)]  # frequency in kHz
        ),
        help="""Unlock Frequency.

        Format:
        ULF,[FRQ] - Unlock a frequency

        Parameters:
        FRQ : Frequency to unlock (25000-512000 kHz)

        Examples:
        ULF,155625 - Unlock 155.625 MHz

        Notes:
        - Removes the specified frequency from the global lockout list
        - This command is only acceptable in Programming Mode
        """,
    ),
}

# Set source module for each command
for cmd in CHANNEL_COMMANDS.values():
    cmd.source_module = "CHANNEL_COMMANDS"
