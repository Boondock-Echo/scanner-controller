"""
Talkgroup Management commands for the BCD325P2.

These commands allow you to create, modify, and manage talkgroup IDs in trunked
 radio systems.
"""

from utilities.core.shared_utils import ScannerCommand
from utilities.validators import validate_param_constraints

TALKGROUP_COMMANDS = {
    "AGT": ScannerCommand(
        name="AGT",
        requires_prg=True,
        set_format="AGT,{system_index}",
        validator=validate_param_constraints([(int, None)]),  # system_index
        help="""Append TGID Group.

        Format:
        AGT,[SYSTEM_INDEX] - Append a TGID group to a system

        Parameters:
        SYSTEM_INDEX : Index of the system to add a TGID group to

        Returns:
        The index of the created TGID group, or -1 if creation failed
        """,
    ),
    "ACT": ScannerCommand(
        name="ACT",
        requires_prg=True,
        set_format="ACT,{group_index}",
        validator=validate_param_constraints([(int, None)]),  # group_index
        help="""Append TGID.

        Format:
        ACT,[GROUP_INDEX] - Append a TGID to a group

        Parameters:
        GROUP_INDEX : Index of the TGID group to add a TGID to

        Returns:
        The index of the created TGID, or -1 if creation failed
        """,
    ),
    "TIN": ScannerCommand(
        name="TIN",
        requires_prg=True,
        set_format=(
            "TIN,{index},{name},{tgid},{lout},{pri},{alt},{altl},{rsv},"
            "{audio_type},{number_tag},{alt_color},{alt_pattern},{vol_offset},"
            "{tdma_slot}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # index
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (str, None),  # tgid (depends on system type)
                (int, {0, 1}),  # lout (0=Unlocked, 1=Lockout)
                (int, {0, 1}),  # pri (0=OFF, 1=ON)
                (
                    int,
                    lambda x: x == 0 or 1 <= x <= 9,
                ),  # alt (0=OFF, 1-9=Tone No)
                (int, lambda x: x == 0 or 1 <= x <= 15),  # altl (0=AUTO, 1-15)
                (str, None),  # rsv (reserved parameter)
                (
                    int,
                    {0, 1, 2},
                ),  # audio_type (0=All, 1=Analog Only, 2=Digital Only)
                (
                    str,
                    lambda x: x == "NONE" or 0 <= int(x) <= 999,
                ),  # number_tag
                (str, {"OFF", "RED"}),  # alt_color
                (int, {0, 1, 2}),  # alt_pattern (0=ON, 1=Slow, 2=Fast)
                (int, (-3, 3)),  # vol_offset (-3 to +3)
                (str, {"ANY", "1", "2"}),  # tdma_slot (ANY, 1, 2)
            ]
        ),
        help="""Get/Set TGID Info.

        Format:
        TIN,[INDEX] - Get TGID information
        TIN,[INDEX],[NAME],[TGID],[LOUT],[PRI],[ALT],[ALTL],[RSV],[AUDIO_TYPE],
        [NUMBER_TAG],[ALT_COLOR],[ALT_PATTERN],[VOL_OFFSET],[TDMA_SLOT] - Set
        TGID

        Parameters:
        INDEX : TGID Index
        NAME : Name (max 16 chars)
        TGID : Talkgroup ID
        LOUT : Lockout (0=Unlocked, 1=Lockout)
        PRI : Priority (0=OFF, 1=ON)
        ALT : Alert Tone (0=OFF, 1-9=Tone No)
        ALTL : Alert Tone Level (0=AUTO, 1-15)
        RSV : Reserved parameter
        AUDIO_TYPE : Audio Type (0=All, 1=Analog Only, 2=Digital Only)
        NUMBER_TAG : Number tag (0-999, NONE)
        ALT_COLOR : Alert Light color (OFF, RED)
        ALT_PATTERN : Alert Light Pattern (0=ON, 1=Slow, 2=Fast)
        VOL_OFFSET : Volume Offset (-3 to +3)
        TDMA_SLOT : TDMA Slot (ANY=Any, 1=Slot 1, 2=Slot 2)

        Returns:
        Detailed TGID information when used in get mode
        """,
    ),
    "GLI": ScannerCommand(
        name="GLI",
        requires_prg=True,
        set_format="GLI,{system_index}",
        validator=validate_param_constraints([(int, None)]),  # system_index
        help="""Get Lockout TGID (for Rvw L/O ID).

        Format:
        GLI,[SYSTEM_INDEX] - Get a locked out TGID from a system

        Parameters:
        SYSTEM_INDEX : System index to get locked out TGIDs from

        Returns:
        A locked out TGID, or -1 when no more lockout TGIDs exist

        Note:
        Call this command repeatedly to get all locked out TGIDs until it
        returns -1
        """,
    ),
    "SLI": ScannerCommand(
        name="SLI",
        requires_prg=True,
        set_format="SLI,{system_index}",
        validator=validate_param_constraints([(int, None)]),  # system_index
        help="""Get Search L/O TGID.

        Format:
        SLI,[SYSTEM_INDEX] - Get a search locked out TGID from a system

        Parameters:
        SYSTEM_INDEX : System index to get search locked out TGIDs from

        Returns:
        A search locked out TGID, or -1 when no more lockout TGIDs exist

        Note:
        Returns only TGIDs that don't belong to any group in the system
        Call this command repeatedly to get all search locked out TGIDs until
        it returns -1
        """,
    ),
    "ULI": ScannerCommand(
        name="ULI",
        requires_prg=True,
        set_format="ULI,{system_index},{tgid}",
        validator=validate_param_constraints(
            [(int, None), (str, None)]  # system_index  # tgid
        ),
        help="""Unlock TGID (for Rvw L/O ID).

        Format:
        ULI,[SYSTEM_INDEX],[TGID] - Unlock a locked out TGID

        Parameters:
        SYSTEM_INDEX : System index containing the locked out TGID
        TGID : Talkgroup ID to unlock

        Note:
        The TGID is removed from the system's lockout list
        """,
    ),
    "LOI": ScannerCommand(
        name="LOI",
        requires_prg=True,
        set_format="LOI,{system_index},{tgid}",
        validator=validate_param_constraints(
            [(int, None), (str, None)]  # system_index  # tgid
        ),
        help="""Lockout ID (TGID).

        Format:
        LOI,[SYSTEM_INDEX],[TGID] - Lock out a TGID

        Parameters:
        SYSTEM_INDEX : System index to add the lockout TGID to
        TGID : Talkgroup ID to lock out

        Note:
        The TGID is added to the system's lockout list
        """,
    ),
}

# Set source module for each command
for cmd in TALKGROUP_COMMANDS.values():
    cmd.source_module = "TALKGROUP_COMMANDS"
