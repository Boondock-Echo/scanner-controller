"""
System Configuration commands for the BCD325P2.

These commands allow you to create, modify, delete, and manage scanner systems.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

SYSTEM_CONFIGURATION_COMMANDS = {
    "CSY": scanner_command(
        name="CSY",
        requires_prg=True,
        set_format="CSY,{sys_type},{protect}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    {
                        "CNV",  # CONVENTIONAL
                        "MOT",  # MOTOROLA TYPE
                        "EDC",  # EDACS Narrow / Wide
                        "EDS",  # EDACS SCAT
                        "LTR",  # LTR
                        "P25S",  # P25 STANDARD (Phase 1/Phase 2/X2-TDMA)
                        "P25F",  # P25 One Frequency TRUNK
                        "TRBO",  # MotoTRBO
                        "DMR",  # DMR One Frequency Trunk
                    },
                ),  # system type
                (int, {0, 1}),  # protect bit status (0=OFF, 1=ON)
            ]
        ),
        help="""Create System.

        Format:
        CSY,[SYS_TYPE],[PROTECT] - Create a new system

        Parameters:
        SYS_TYPE : System Type
            CNV : CONVENTIONAL
            MOT : MOTOROLA TYPE
            EDC : EDACS Narrow / Wide
            EDS : EDACS SCAT
            LTR : LTR
            P25S : P25 STANDARD (Phase 1/Phase 2/X2-TDMA)
            P25F : P25 One Frequency TRUNK
            TRBO : MotoTRBO
            DMR : DMR One Frequency Trunk
        PROTECT : Protect bit status (0=OFF, 1=ON)

        Returns:
        The index of the created system, or -1 if creation failed due to
        insufficient resources
        """,
    ),
    "DSY": scanner_command(
        name="DSY",
        requires_prg=True,
        set_format="DSY,{sys_index}",
        validator=validate_param_constraints([(int, None)]),  # system index
        help="""Delete System.

        Format:
        DSY,[SYS_INDEX] - Delete a system

        Parameters:
        SYS_INDEX : System Index to delete
        """,
    ),
    "SIN": scanner_command(
        name="SIN",
        requires_prg=True,
        set_format=(
            "SIN,{index},{name},{quick_key},{hld},{lout},{dly},"
            "{start_key},{number_tag},{agc_analog},{agc_digital},{p25waiting}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # index
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (str, lambda x: x == "." or 0 <= int(x) <= 99),  # quick_key
                (int, (0, 255)),  # hold time
                (int, {0, 1}),  # lockout
                (
                    str,
                    {"-10", "-5", "-2", "0", "1", "2", "5", "10", "30"},
                ),  # delay time
                (str, lambda x: x == "." or 0 <= int(x) <= 9),  # startup key
                (
                    str,
                    lambda x: x == "NONE" or 0 <= int(x) <= 999,
                ),  # number tag
                (int, {0, 1}),  # analog AGC
                (int, {0, 1}),  # digital AGC
                (
                    int,
                    {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000},
                ),  # P25 waiting time
            ]
        ),
        help="""Get/Set System Information.

        Format:
        SIN,[INDEX] - Get system information
        SIN,[INDEX],[NAME],[QUICK_KEY],[HLD],[LOUT],[DLY],...,[NUMBER_TAG],
        [AGC_ANALOG],[AGC_DIGITAL],[P25WAITING] - Set system information

        Parameters:
        INDEX : System Index
        NAME : Name (max 16 chars)
        QUICK_KEY : Quick Key (0-99, . for none)
        HLD : System Hold Time (0-255)
        LOUT : Lockout (0=Unlocked, 1=Lockout)
        DLY : Delay Time (-10,-5,-2,0,1,2,5,10,30)
        START_KEY : Startup Configuration Key (0-9, . for none)
        NUMBER_TAG : Number tag (0-999, NONE)
        AGC_ANALOG : AGC Setting for Analog Audio (0=OFF, 1=ON)
        AGC_DIGITAL : AGC Setting for Digital Audio (0=OFF, 1=ON)
        P25WAITING : Digital Waiting time (0,100,200,...,900,1000 ms)

        Returns:
        Detailed system information including type, settings and related indices
        """,
    ),
    "SIH": scanner_command(
        name="SIH",
        requires_prg=True,
        set_format="SIH",
        help="""Get System Index Head.

        Format:
        SIH - Get the first index of stored system list

        Returns:
        The first index in the system list
        """,
    ),
    "SIT": scanner_command(
        name="SIT",
        requires_prg=True,
        set_format="SIT",
        help="""Get System Index Tail.

        Format:
        SIT - Get the last index of stored system list

        Returns:
        The last index in the system list
        """,
    ),
    "SCT": scanner_command(
        name="SCT",
        requires_prg=True,
        set_format="SCT",
        help="""Get System Count.

        Format:
        SCT - Get the number of stored systems

        Returns:
        The number of systems stored in the scanner (0-500)
        """,
    ),
    "QSL": scanner_command(
        name="QSL",
        requires_prg=True,
        set_format=(
            "QSL,{page0},{page1},{page2},{page3},{page4},{page5},"
            "{page6},{page7},{page8},{page9}"
        ),
        validator=validate_param_constraints(
            [
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page0
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page1
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page2
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page3
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page4
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page5
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page6
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page7
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page8
                (
                    str,
                    lambda x: all(c in "012" for c in x) and len(x) == 10,
                ),  # page9
            ]
        ),
        help="""Get/Set System/Site Quick Lockout.

        Format:
        QSL - Get current quick lockout settings
        QSL,[PAGE0],[PAGE1],...,[PAGE9] - Set quick lockout settings

        Parameters:
        PAGE0...PAGE9 : Quick key status (10 characters, each 0/1/2)
                        0 = Not assigned (displayed as "-" on scanner)
                        1 = On (displayed as the number on scanner)
                        2 = Off (displayed as "*" on scanner)

        PAGE0 : Quick Keys 1-9,0 (where 0 means 10)
        PAGE1 : Quick Keys 11-19,10
        ...and so on up to...
        PAGE9 : Quick Keys 91-99,90

        Notes:
        This command cannot turn on/off quick keys that have no System/Site.
        """,
    ),
}
