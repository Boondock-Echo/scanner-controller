"""
Channel Management commands for the BC125AT.

These commands allow you to create, modify, and delete memory channels,
configure channel groups, and control lockout settings. The BC125AT can store
up to 500 conventional channels across 10 banks.
"""

from utilities.core.command_library import ScannerCommand
from utilities.validators import validate_param_constraints

CHANNEL_COMMANDS = {
    "CIN": ScannerCommand(
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
    "DCH": ScannerCommand(
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
}

# Set source module for each command
for cmd in CHANNEL_COMMANDS.values():
    cmd.source_module = "CHANNEL_COMMANDS"
