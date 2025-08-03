"""
Close Call commands for the BC125AT.

Close Call is a feature that allows the scanner to automatically detect and tune
to strong nearby radio transmissions. These commands enable configuration of the
Close Call settings including bands, alerts, and modes.
"""

from utilities.core.command_library import ScannerCommand
from utilities.validators import validate_param_constraints

CLOSE_CALL_COMMANDS = {
    "CLC": ScannerCommand(
        name="CLC",
        requires_prg=True,
        set_format="CLC,{mode},{alert_beep},{alert_light},{cc_band},{lockout}",
        validator=validate_param_constraints(
            [
                (int, {0, 1, 2}),  # mode (0=OFF, 1=CC PRI, 2=CC DND)
                (int, {0, 1}),  # alert beep (0=OFF, 1=ON)
                (int, {0, 1}),  # alert light (0=OFF, 1=ON)
                (
                    str,
                    lambda x: len(x) == 5 and all(c in "01" for c in x),
                ),  # cc_band (5-digit binary mask)
                (int, {0, 1}),  # lockout (0=Unlocked, 1=Lockout)
            ]
        ),
        help="""Get/Set Close Call Settings.

        Format:
        CLC - Get current Close Call settings
        CLC,[CC_MODE],[ALTB],[ALTL],[CC_BAND],[LOUT] - Set Close Call settings

        Parameters:
        CC_MODE : Close Call Mode (0=OFF, 1=CC PRI, 2=CC DND)
        ALTB : Alert Beep (0=OFF, 1=ON)
        ALTL : Alert Light (0=OFF, 1=ON)
        CC_BAND : Close Call Band (5-digit binary mask)
                 Each digit is 0 (OFF) or 1 (ON)
                 Digit positions represent:
                 |||||
                 ||||+--- UHF (400-512 MHz)
                 |||+---- VHF HIGH2 (216-225 MHz)
                 ||+----- VHF HIGH1 (137-174 MHz)
                 |+------ AIR BAND (108-136 MHz)
                 +------- VHF LOW1 (25-54 MHz)
        LOUT : Lockout for Close Call hits with scan (0=Unlocked, 1=Lockout)

        Examples:
        CLC,1,1,1,11111,0
        Set CC Priority mode, all alerts & bands on, no lockout

        CLC,2,1,0,10100,0
        Set CC Do-Not-Disturb mode, beep on, light off,
        VHF LOW1 and VHF HIGH1 bands only, no lockout

        Notes:
        - CC PRI (Priority) interrupts scanning to check for Close Call hits
        - CC DND (Do-Not-Disturb) only checks for Close Call hits during channel
            delays
        - This command is only acceptable in Programming Mode
        """,
    ),
    "SCO": ScannerCommand(
        name="SCO",
        requires_prg=True,
        set_format="SCO,{delay},{code_search}",
        validator=validate_param_constraints(
            [
                (int, {-10, -5, 0, 1, 2, 3, 4, 5}),  # delay time
                (int, {0, 1}),  # CTCSS/DCS search (0=OFF, 1=ON)
            ]
        ),
        help="""Get/Set Search/Close Call Settings.

        Format:
        SCO - Get current Search/Close Call settings
        SCO,[DLY],[CODE_SRCH] - Set Search/Close Call settings

        Parameters:
        DLY : Delay Time (-10, -5, 0, 1, 2, 3, 4, 5)
              Negative values represent -10s and -5s
              0 means no delay
              1-5 represent delay in seconds
        CODE_SRCH : CTCSS/DCS Search (0=OFF, 1=CTCSS/DCS)

        Examples:
        SCO,2,1 - Set 2 second delay, CTCSS/DCS search on
        SCO,0,0 - Set no delay, CTCSS/DCS search off

        Notes:
        - Delay time determines how long scanner stays on a frequency after
            transmission ends
        - CTCSS/DCS search looks for subaudible tones/codes used for squelch
        - This command is only acceptable in Programming Mode
        """,
    ),
}

# Set source module for each command
for cmd in CLOSE_CALL_COMMANDS.values():
    cmd.source_module = "CLOSE_CALL_COMMANDS"
