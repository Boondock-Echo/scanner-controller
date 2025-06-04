"""
Programming Control Commands for the BCD325P2.

These commands control entering and exiting programming mode, which is required
for most configuration commands.
"""

from utilities.core.shared_utils import ScannerCommand

PROGRAMMING_CONTROL_COMMANDS = {
    "PRG": ScannerCommand(
        name="PRG",
        requires_prg=False,
        set_format="PRG",
        help="""Enter Program Mode.

        Format:
        PRG - Enter programming mode

        Notes:
        The scanner will display "Remote Mode" and "Keypad Lock" when in Program
        Mode. This command is invalid when the scanner is in Menu Mode, during
        Direct Entry
        operation, or during Quick Save operation.
        Most configuration commands require the scanner to be in Program Mode.
        """,
    ),
    "EPG": ScannerCommand(
        name="EPG",
        requires_prg=True,
        set_format="EPG",
        help="""Exit Program Mode.

        Format:
        EPG - Exit programming mode

        Notes:
        This command exits Program Mode and returns the scanner to Scan Hold
        Mode.
        """,
    ),
}

# Set source module for each command
for cmd in PROGRAMMING_CONTROL_COMMANDS.values():
    cmd.source_module = "PROGRAMMING_CONTROL_COMMANDS"
