"""
Frequency-related functions for the BCD325P2 scanner.

Contains functions for reading and setting frequencies.
"""

import time

from decimal import Decimal
from adapters.uniden.common.constants import (
    HZ_PER_MHZ,
    HZ_PER_SCANNER_UNIT,
    SCANNER_UNITS_PER_MHZ,
)
from adapters.uniden.common.core import ensure_str


def read_frequency(self, ser):
    """Read the current frequency from the BCD325P2.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Frequency information or error message.
    """
    try:
        response = self.send_command(ser, "PWR")
        response_str = ensure_str(response)

        parts = response_str.strip().split(",")
        if len(parts) >= 3 and parts[0] == "PWR":
            freq_mhz = (int(parts[2]) * HZ_PER_SCANNER_UNIT) / HZ_PER_MHZ
            return self.feedback(True, f"Frequency: {freq_mhz} MHz")
        return self.feedback(False, f"Unexpected response: {response_str}")
    except Exception as e:
        return self.feedback(False, f"Error reading frequency: {e}")


def write_frequency(self, ser, freq):
    """Set the frequency.

    Args:
        ser: Serial connection to the scanner.
        freq: Frequency to set in MHz. The value will be converted to
            100 Hz units for the command.

    Returns:
        str: Status message after frequency entry.
    """
    try:
        # Convert frequency to 100 Hz units for the scanner
        freq_100hz = int(Decimal(freq) * SCANNER_UNITS_PER_MHZ)

        # Use QSH command to tune to the frequency
        response = self.send_command(ser, f"QSH,{freq_100hz},AUTO,0")
        response_str = ensure_str(response)

        if "OK" in response_str:
            return self.feedback(True, f"Frequency set to {freq} MHz")
        return self.feedback(False, f"Error setting frequency: {response_str}")
    except Exception as e:
        return self.feedback(False, f"Error setting frequency: {e}")


def enter_quick_frequency_hold(self, ser, freq_mhz):
    """Enter a frequency in quick hold mode.

    Args:
        ser: Serial connection to the scanner.
        freq_mhz: Frequency in MHz. This value will be converted to
            100 Hz units for the command.

    Returns:
        str: Status message after frequency entry.
    """
    try:
        # Convert frequency to 100 Hz units for the scanner
        freq_100hz = int(Decimal(freq_mhz) * SCANNER_UNITS_PER_MHZ)

        # Use QSH command directly
        response = self.send_command(ser, f"QSH,{freq_100hz},AUTO,0")
        response_str = ensure_str(response)

        if "OK" in response_str:
            # Verify the frequency was set
            time.sleep(0.3)
            verify_response = self.send_command(ser, "PWR")
            verify_str = ensure_str(verify_response)
            parts = verify_str.strip().split(",")

            if len(parts) >= 3 and parts[0] == "PWR":
                actual_freq = int(parts[2]) / SCANNER_UNITS_PER_MHZ
                if (
                    abs(actual_freq - freq_mhz) < 0.05
                ):  # Allow for small rounding differences
                    return self.feedback(
                        True,
                        f"✅ Frequency {freq_mhz} MHz entered and confirmed "
                        f"({actual_freq:.5f} MHz)",
                    )
                else:
                    return self.feedback(
                        False,
                        f"⚠️ Entered {freq_mhz} MHz, but scanner reports "
                        f"{actual_freq:.5f} MHz",
                    )
            return self.feedback(True, f"Frequency set to {freq_mhz} MHz")
        return self.feedback(
            False, f"❌ Error setting frequency: {response_str}"
        )
    except Exception as e:
        return self.feedback(False, f"❌ Error in quick frequency hold: {e}")
