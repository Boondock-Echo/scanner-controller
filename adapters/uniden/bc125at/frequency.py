"""
Frequency-related functions for the BC125AT scanner.

Contains functions for reading and setting frequencies.
"""

import time

from adapters.uniden.common.core import ensure_str
from utilities.scanner.backend import send_command


def read_frequency(self, ser):
    """Read the current frequency from the BC125AT.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Frequency information or error message.
    """
    try:
        response = self.send_command(ser, "PWR")
        response_str = ensure_str(response)

        parts = response_str.strip().split(",")
        if len(parts) == 3 and parts[0] == "PWR":
            freq_mhz = (int(parts[2]) * 100) / 1_000_000
            return self.feedback(True, f"Frequency: {freq_mhz} MHz")
        return self.feedback(False, f"Unexpected response: {response_str}")
    except Exception as e:
        return self.feedback(False, f"Error reading frequency: {e}")


def write_frequency(self, ser, freq):
    """Set frequency (not directly supported on BC125AT).

    Args:
        ser: Serial connection to the scanner.
        freq: Frequency to set.

    Returns:
        str: Error message indicating feature not supported.
    """
    return self.feedback(
        False, "Frequency input not supported via direct command."
    )


def enter_quick_frequency_hold(self, ser, freq_mhz):
    """Enter a frequency in quick hold mode.

    Args:
        ser: Serial connection to the scanner.
        freq_mhz: Frequency in MHz.

    Returns:
        str: Status message after frequency entry.
    """
    try:
        send_command(ser, "PRG")
        time.sleep(0.2)
        send_command(ser, "EPG")
        time.sleep(0.2)
        send_command(ser, "KEY,S,P")
        time.sleep(0.1)
        send_command(ser, "KEY,S,P")
        time.sleep(0.1)
        send_command(ser, "KEY,H,P")
        time.sleep(0.1)
        freq_str = f"{freq_mhz:.3f}"
        for char in freq_str:
            if char in "0123456789.":
                send_command(ser, f"KEY,{char},P")
                time.sleep(0.05)
        send_command(ser, "KEY,H,P")
        time.sleep(0.3)
        response = send_command(ser, "PWR")
        response_str = ensure_str(response)

        parts = response_str.strip().split(",")
        if len(parts) == 3 and parts[0] == "PWR":
            actual_freq = int(parts[2]) / 10000.0
            if abs(actual_freq - freq_mhz) < 0.005:
                return self.feedback(
                    True,
                    f"Frequency {freq_str} MHz entered and confirmed via PWR "
                    f"({actual_freq:.5f} MHz)",
                )
            else:
                return self.feedback(
                    False,
                    f"Entered {freq_str} MHz, but PWR returned "
                    f"{actual_freq:.5f} MHz",
                )
        return self.feedback(False, f"PWR returned unexpected: {response_str}")
    except Exception as e:
        return self.feedback(False, f"Quick Frequency Hold Error: {e}")
