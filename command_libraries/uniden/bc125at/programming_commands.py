"""
Programming mode control commands for the BC125AT.

These commands handle entering and exiting the scanner's programming mode,
which is required for most configuration operations.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

PROGRAMMING_COMMANDS = {
    "PRG": scanner_command(
        name="PRG",
        requires_prg=False,
        set_format="PRG",
        validator=validate_param_constraints([]),  # no parameters
        help="""Enter Programming Mode.

        Format:
        PRG - Enter scanner programming mode

        Response:
        PRG,OK - Successfully entered programming mode
        PRG,NG - Failed to enter programming mode

        Notes:
        - The scanner displays "Remote Mode" on first line and "Keypad Lock" on
            second line
        - This command is invalid when the scanner is in Menu Mode, during
            Direct Entry operation,
          or during Quick Save operation
        - Many commands require the scanner to be in programming mode
        """,
    ),
    "EPG": scanner_command(
        name="EPG",
        requires_prg=True,
        set_format="EPG",
        validator=validate_param_constraints([]),  # no parameters
        help="""Exit Programming Mode.

        Format:
        EPG - Exit scanner programming mode

        Response:
        EPG,OK - Successfully exited programming mode

        Notes:
        - The scanner exits from Program Mode and goes to Scan Hold Mode
        - All programming mode only commands will be unavailable after this
            command
        """,
    ),
    # Placeholders for missing commands
    # "FWM": scanner_command(
    #     name="FWM",
    #     requires_prg=True,
    #     set_format="FWM,{address},{data}",
    #     validator=validate_param_constraints([]),
    #     help="""Firmware Memory Access.
    #
    #     Format:
    #     FWM,[ADDRESS] - Get firmware memory at address
    #     FWM,[ADDRESS],[DATA] - Set firmware memory at address
    #     """,
    # ),
    # "MMM": scanner_command(
    #     name="MMM",
    #     requires_prg=True,
    #     set_format="MMM,{option}",
    #     validator=validate_param_constraints([]),
    #     help="""Memory Mode Menu.
    #
    #     Format:
    #     MMM - Get memory mode
    #     MMM,[OPTION] - Set memory mode option
    #     """,
    # ),
    # "MWR": scanner_command(
    #     name="MWR",
    #     requires_prg=True,
    #     set_format="MWR,{address},{data}",
    #     validator=validate_param_constraints([]),
    #     help="""Memory Write.
    #
    #     Format:
    #     MWR,[ADDRESS],[DATA] - Write data to memory address
    #     """,
    # ),
    "MRD": scanner_command(
        name="MRD",
        requires_prg=True,
        set_format="MRD,{address}",
        validator=validate_param_constraints([]),
        help="""Memory Read.
            Format:
        MRD,[ADDRESS] - Read data from memory address
        """,
    ),
    # "JPM": scanner_command(
    #     name="JPM",
    #     requires_prg=False,
    #     set_format="JPM,{menu_item}",
    #     validator=validate_param_constraints([]),
    #     help="""Jump to Menu.
    #
    #     Format:
    #     JPM,[MENU_ITEM] - Jump to specific menu item
    #     """,
    # ),
    # "PDI": scanner_command(
    #     name="PDI",
    #     requires_prg=True,
    #     set_format="PDI,{setting}",
    #     validator=validate_param_constraints([]),
    #     help="""Programming Device Initialization.
    #
    #     Format:
    #     PDI - Get programming device settings
    #     PDI,[SETTING] - Initialize programming device
    #     """,
    # ),
    # "EWP": scanner_command(
    #     name="EWP",
    #     requires_prg=True,
    #     set_format="EWP,{setting}",
    #     validator=validate_param_constraints([]),
    #     help="""EEPROM Write Protect.
    #
    #     Format:
    #     EWP - Get EEPROM write protect status
    #     EWP,[SETTING] - Set EEPROM write protect
    #     """,
    # ),
}

# Set source module for each command
for cmd in PROGRAMMING_COMMANDS.values():
    cmd.source_module = "PROGRAMMING_COMMANDS"
