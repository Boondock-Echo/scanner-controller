"""
Channel and Group Management commands for the BCD325P2.

These commands allow you to create, modify, and delete channels and groups.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

CHANNEL_GROUP_COMMANDS = {
    "AGC": scanner_command(
        name="AGC",
        requires_prg=True,
        set_format="AGC,{group_index},{name},{quick_key},{lout}",
        validator=validate_param_constraints(
            [
                (int, None),  # group_index
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (
                    str,
                    lambda x: x == "." or 0 <= int(x) <= 99,
                ),  # quick_key (0-99, .)
                (int, {0, 1}),  # lout (0=Unlocked, 1=Lockout)
            ]
        ),
        help="""Add Group to Conventional System.

        Format:
        AGC,[INDEX],[NAME],[QUICK_KEY],[LOUT] - Add a group to a conventional
        system

        Parameters:
        INDEX : Index number for the group
        NAME : Name (max 16 chars)
        QUICK_KEY : Quick key (0-99, . for none)
        LOUT : Lockout (0=Unlocked, 1=Lockout)
        """,
    ),
    "DGR": scanner_command(
        name="DGR",
        requires_prg=True,
        set_format="DGR,{system_index},{group_index}",
        validator=validate_param_constraints(
            [(int, None), (int, None)]  # system_index  # group_index
        ),
        help="""Delete Group.

        Format:
        DGR,[SYSTEM_INDEX],[GROUP_INDEX] - Delete a group

        Parameters:
        SYSTEM_INDEX : Index of the system containing the group
        GROUP_INDEX : Index of the group to delete
        """,
    ),
    "GIN": scanner_command(
        name="GIN",
        requires_prg=True,
        set_format="GIN,{system_index},{group_index}",
        validator=validate_param_constraints(
            [(int, None), (int, None)]  # system_index  # group_index
        ),
        help="""Get Group Information.

        Format:
        GIN,[SYSTEM_INDEX],[GROUP_INDEX] - Get information about a group

        Parameters:
        SYSTEM_INDEX : Index of the system containing the group
        GROUP_INDEX : Index of the group to get information about

        Returns:
        Group information including name, quick key, and lockout status
        """,
    ),
    "ACC": scanner_command(
        name="ACC",
        requires_prg=True,
        set_format=(
            "ACC,{system_index},{group_index},{channel_index},{name},{freq},"
            "{mod},{ctcss_dcs},{tlock},{lout},{pri},{att},{alt_color},"
            "{alt_pattern}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # system_index
                (int, None),  # group_index
                (int, None),  # channel_index
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (int, None),  # frequency
                (str, {"AUTO", "AM", "FM", "NFM", "WFM"}),  # modulation
                (str, None),  # ctcss/dcs
                (int, {0, 1}),  # tone lockout
                (int, {0, 1}),  # lockout
                (int, {0, 1}),  # priority
                (int, {0, 1}),  # attenuation
                (
                    str,
                    {
                        "OFF",
                        "RED",
                        "BLUE",
                        "MAGENTA",
                        "GREEN",
                        "CYAN",
                        "YELLOW",
                        "WHITE",
                    },
                ),  # alert color
                (int, {0, 1, 2}),  # alert pattern (0=ON, 1=Slow, 2=Fast)
            ]
        ),
        help="""Add Channel to Conventional System.

        Format:
        ACC,[SYSTEM_INDEX],[GROUP_INDEX],[CHANNEL_INDEX],[NAME],... -
        Add a channel

        Parameters:
        SYSTEM_INDEX : Index of the system
        GROUP_INDEX : Index of the group within the system
        CHANNEL_INDEX : Index for the new channel
        NAME : Name of the channel (max 16 chars)
        FREQ : Frequency in Hz
        MOD : Modulation (AUTO, AM, FM, NFM, WFM)
        CTCSS_DCS : CTCSS/DCS code (e.g., 127.3, 127.3N, 127.3I, D023, D023N,
             D023I)
        TLOCK : Tone lockout (0=OFF, 1=ON)
        LOUT : Lockout (0=Unlocked, 1=Lockout)
        PRI : Priority (0=OFF, 1=ON)
        ATT : Attenuation (0=OFF, 1=ON)
        ALT_COLOR : Alert light color
        ALT_PATTERN : Alert light pattern (0=ON, 1=Slow, 2=Fast)
        """,
    ),
    "DCH": scanner_command(
        name="DCH",
        requires_prg=True,
        set_format="DCH,{system_index},{group_index},{channel_index}",
        validator=validate_param_constraints(
            [
                (int, None),  # system_index
                (int, None),  # group_index
                (int, None),  # channel_index
            ]
        ),
        help="""Delete Channel.

        Format:
        DCH,[SYSTEM_INDEX],[GROUP_INDEX],[CHANNEL_INDEX] - Delete a channel

        Parameters:
        SYSTEM_INDEX : Index of the system containing the channel
        GROUP_INDEX : Index of the group containing the channel
        CHANNEL_INDEX : Index of the channel to delete
        """,
    ),
    "CIN": scanner_command(
        name="CIN",
        requires_prg=True,
        set_format="CIN,{system_index},{group_index},{channel_index}",
        validator=validate_param_constraints(
            [
                (int, None),  # system_index
                (int, None),  # group_index
                (int, None),  # channel_index
            ]
        ),
        help="""Get Channel Information.

        Format:
        CIN,[SYSTEM_INDEX],[GROUP_INDEX],[CHANNEL_INDEX] - Get channel
             information

        Parameters:
        SYSTEM_INDEX : Index of the system containing the channel
        GROUP_INDEX : Index of the group containing the channel
        CHANNEL_INDEX : Index of the channel to get information about

        Returns:
        Channel information including name, frequency, modulation type and
             settings
        """,
    ),
    "QGL": scanner_command(
        name="QGL",
        requires_prg=False,
        set_format="QGL,{quick_key},{lockout}",
        validator=validate_param_constraints(
            [
                (int, (0, 99)),  # quick_key (0-99)
                (int, {0, 1}),  # lockout (0=Unlock, 1=Lockout)
            ]
        ),
        help="""Quick Group Lockout.

        Format:
        QGL,[QUICK_KEY],[LOCKOUT] - Set quick group lockout status

        Parameters:
        QUICK_KEY : Quick key number (0-99)
        LOCKOUT : Lockout status (0=Unlock, 1=Lockout)

        Notes:
        This command allows you to quickly lock out all systems/sites/searches
        that are assigned to the specified quick key.
        """,
    ),
}

# Set source module for each command
for cmd in CHANNEL_GROUP_COMMANDS.values():
    cmd.source_module = "CHANNEL_GROUP_COMMANDS"
