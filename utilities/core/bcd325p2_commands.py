"""
BCD325P2 Commands module.

This module defines the commands for the BCD325P2 scanner.
"""

from utilities.core.shared_utils import scanner_command

commands = {
    "PWR": scanner_command(
        name="PWR",
        help="Returns RSSI and frequency. Format: PWR,<rssi>,<freq>.",
    ),
    "BAV": scanner_command(
        name="BAV", help="Returns battery voltage in 100's of milliVolts."
    ),
    "WIN": scanner_command(
        name="WIN", help="Returns window voltage and frequency."
    ),
    "STS": scanner_command(
        name="STS",
        help="Returns status display content and various system flags.",
    ),
    "GLF": scanner_command(
        name="GLF",
        requires_prg=True,
        help="Get next Global Lockout Frequency. Repeat until GLF,-1.",
    ),
    "CIN": scanner_command(
        name="CIN",
        requires_prg=True,
        help="Get or set channel info. Format: CIN,<index>[,...].",
    ),
    "QSH": scanner_command(
        name="QSH", help="Quick search/hold mode. Format: QSH,<freq_kHz>."
    ),
}
