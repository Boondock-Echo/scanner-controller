"""
Frequency Management commands for the BCD325P2.

These commands allow you to program, manage, and control frequencies on the
scanner.
"""

from utilities.core.shared_utils import ScannerCommand
from utilities.validators import validate_param_constraints

FREQUENCY_MANAGEMENT_COMMANDS = {
    "BLT": ScannerCommand(
        name="BLT",
        requires_prg=True,
        set_format="BLT,{band_number}",
        validator=validate_param_constraints(
            [(int, (1, 31))]  # band_number (1-31)
        ),
        help="""Band Lookup Table.

        Format:
        BLT - Get current band information
        BLT,[BAND_NUMBER] - Get information for specific band number

        Parameters:
        BAND_NUMBER : Band number (1-31)

        Returns:
        Lower limit, upper limit, step, offset, and modulation for the band
        """,
    ),
    "BSV": ScannerCommand(
        name="BSV",
        requires_prg=False,
        set_format="BSV,{sweep_operation}",
        validator=validate_param_constraints(
            [(int, {0, 1, 2})]  # sweep_operation (0=Stop, 1=Start, 2=View)
        ),
        help="""Band Scope Sweep Control.

        Format:
        BSV,[SWEEP_OPERATION] - Control band scope sweep

        Parameters:
        SWEEP_OPERATION : Operation (0=Stop, 1=Start, 2=View)
        """,
    ),
    "CNT": ScannerCommand(
        name="CNT",
        requires_prg=False,
        set_format="CNT,{frequency}",
        validator=validate_param_constraints([(int, None)]),  # frequency in Hz
        help="""Frequency Counter.

        Format:
        CNT - Get current frequency counter reading
        CNT,[FREQUENCY] - Set center frequency for the counter

        Parameters:
        FREQUENCY : Center frequency in Hz
        """,
    ),
    "OMS": ScannerCommand(
        name="OMS",
        requires_prg=True,
        set_format=(
            "OMS,{squelch_mode},{rsv1},{pll_step},{mute_analog},"
            "{mute_digital},{digital_agc},{rsv2}"
        ),
        validator=validate_param_constraints(
            [
                (int, {0, 1}),  # squelch_mode (0=Normal, 1=Open)
                (str, None),  # reserved
                (int, {0, 1}),  # pll_step (0=5kHz/6.25kHz, 1=Auto)
                (int, {0, 1}),  # mute_analog (0=OFF, 1=ON)
                (int, {0, 1}),  # mute_digital (0=OFF, 1=ON)
                (int, {0, 1}),  # digital_agc (0=OFF, 1=ON)
                (str, None),  # reserved
            ]
        ),
        help="""Get/Set Output Mode Select.

        Format:
        OMS - Get current output mode settings
        OMS,[SQUELCH_MODE],[RSV],[PLL_STEP],[MUTE_ANALOG],[MUTE_DIGITAL],
        [DIGITAL_AGC],[RSV]

        Parameters:
        SQUELCH_MODE : Squelch mode (0=Normal, 1=Open)
        RSV : Reserved parameter
        PLL_STEP : PLL step setting (0=5kHz/6.25kHz, 1=Auto)
        MUTE_ANALOG : Mute analog audio (0=OFF, 1=ON)
        MUTE_DIGITAL : Mute digital audio (0=OFF, 1=ON)
        DIGITAL_AGC : Digital AGC (0=OFF, 1=ON)
        RSV : Reserved parameter
        """,
    ),
    "GLF": ScannerCommand(
        name="GLF",
        requires_prg=True,
        set_format="GLF",
        help="""Get Lockout Frequencies.

        Format:
        GLF - Get list of locked out frequencies

        Returns:
        List of frequencies that are locked out in the current search range
        """,
    ),
    "ULF": ScannerCommand(
        name="ULF",
        requires_prg=True,
        set_format="ULF,{frequency}",
        validator=validate_param_constraints([(int, None)]),  # frequency in Hz
        help="""Unlock Frequency.

        Format:
        ULF,[FREQUENCY] - Unlock a previously locked out frequency

        Parameters:
        FREQUENCY : Frequency in Hz to unlock
        """,
    ),
    "LOF": ScannerCommand(
        name="LOF",
        requires_prg=True,
        set_format="LOF,{frequency}",
        validator=validate_param_constraints([(int, None)]),  # frequency in Hz
        help="""Lockout Frequency.

        Format:
        LOF,[FREQUENCY] - Lock out a frequency

        Parameters:
        FREQUENCY : Frequency in Hz to lock out
        """,
    ),
    "GIE": ScannerCommand(
        name="GIE",
        requires_prg=True,
        set_format="GIE",
        help="""Get IF Exchange.

        Format:
        GIE - Get current IF exchange settings

        Returns:
        List of IF exchange frequencies and settings
        """,
    ),
    "CIE": ScannerCommand(
        name="CIE",
        requires_prg=True,
        set_format="CIE,{index},{frequency_from},{frequency_to}",
        validator=validate_param_constraints(
            [
                (int, (0, 9)),  # index (0-9)
                (int, None),  # frequency_from in Hz
                (int, None),  # frequency_to in Hz
            ]
        ),
        help="""Change IF Exchange.

        Format:
        CIE,[INDEX],[FREQUENCY_FROM],[FREQUENCY_TO] - Change an IF exchange
        entry

        Parameters:
        INDEX : Index of the exchange entry (0-9)
        FREQUENCY_FROM : Original frequency in Hz
        FREQUENCY_TO : Replacement frequency in Hz
        """,
    ),
    "RIE": ScannerCommand(
        name="RIE",
        requires_prg=True,
        set_format="RIE,{index}",
        validator=validate_param_constraints([(int, (0, 9))]),  # index (0-9)
        help="""Reset IF Exchange.

        Format:
        RIE,[INDEX] - Reset an IF exchange entry

        Parameters:
        INDEX : Index of the exchange entry to reset (0-9)
        """,
    ),
}

# Set source module for each command
for cmd in FREQUENCY_MANAGEMENT_COMMANDS.values():
    cmd.source_module = "FREQUENCY_MANAGEMENT_COMMANDS"
