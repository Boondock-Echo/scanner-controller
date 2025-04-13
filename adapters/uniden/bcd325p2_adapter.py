# Import utility for progress bar
"""
Bcd325P2 Adapter module.

This module provides functionality related to bcd325p2 adapter.
"""

# Standard library imports
import sys

# Application imports
from adapters.uniden.uniden_base_adapter import UnidenScannerAdapter

# Import commands directly from the decoupled module
from utilities.core.bcd325p2_commands import commands


def hex32(value):
    """
    Convert an integer to a 32-bit hexadecimal string without the '0x' prefix.

    Args:
        value (int): The integer value to be converted.
    Returns:
        str: A 32-bit hexadecimal string representation of the input integer.
    """
    # Convert an integer to a 32-bit hexadecimal string without the '0x' prefix

    return f"{value:08X}"


def update_progress(current, total):
    """Display a progress bar for long-running operations."""
    percent = int(100 * current / total)
    bar = "#" * (percent // 2)
    sys.stdout.write(f"\rProgress: [{bar:<50}] {percent}%")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")
        sys.stdout.flush()


class BCD325P2Adapter(UnidenScannerAdapter):
    """Adapter for the BCD325P2 scanner."""

    def __init__(self, machine_mode=False):
        """Initialize the BCD325P2 adapter.

        Args:
            machine_mode: Whether to use machine-readable output format.
        """
        super().__init__(machine_mode, commands)
        # Set the scanner model identifier to ensure compatibility
        # with parent class methods
        self.machine_mode_id = "BCD325P2"

    def feedback(self, success, message):
        """Format feedback based on machine_mode setting."""
        if (
            self.machine_mode
        ):  # Use machine_mode instead of machine_mode_id for consistency
            return "OK" if success else "ERROR"
        return message

    def get_help(self, command):
        """
        Get help for a specific BCD325P2 command.

        Args:
            command: The command to get help for.

        Returns:
            String containing help text for the specified command.
        """
        try:
            cmd = self.commands.get(command.upper())
            if not cmd:
                return f"Command '{command}' not found in command library"
            if not hasattr(cmd, "help") or not cmd.help:
                return f"No help available for command '{command}'"
            return cmd.help
        except Exception as e:
            return self.feedback(False, f"Error retrieving help: {e}")

    def read_rssi(self, ser):
        """Read the signal strength from the BCD325P2."""
        try:
            response = self.send_command(
                ser, self.commands["PWR"].buildCommand()
            )
            response_str = self.ensure_str(
                response
            )  # Ensure we convert to string
            parts = response_str.split(",")
            if len(parts) == 3:
                return round(int(parts[1]) / 1023.0, 3)
            return self.feedback(
                False, f"Unexpected PWR response: {response_str}"
            )
        except Exception as e:
            return self.feedback(False, f"Error reading RSSI: {e}")

    def read_battery_voltage(self, ser):
        """Read the battery voltage from the BCD325P2."""
        try:
            response = self.send_command(
                ser, self.commands["BAV"].buildCommand()
            )
            _, val = response.split(",")
            voltage = (3.2 * int(val) * 2) / 1023
            return round(voltage, 3)
        except Exception as e:
            return self.feedback(False, f"Error reading battery voltage: {e}")

    def read_window_voltage(self, ser):
        """Read the window voltage from the BCD325P2."""
        try:
            return self.send_command(ser, self.commands["WIN"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading window voltage: {e}")

    def read_status(self, ser):
        """Read the scanner status from the BCD325P2."""
        try:
            return self.send_command(ser, self.commands["STS"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading status: {e}")

    def read_s_meter(self, ser):
        """S-meter (not supported on BCD325P2)."""
        return self.feedback(False, "S-Meter not supported on BCD325P2")

    def read_frequency(self, ser):
        """Read the current frequency from the BCD325P2."""
        try:
            response = self.send_command(ser, "PWR")
            response_str = self.ensure_str(response)  # Convert bytes to string
            parts = response_str.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                return self.feedback(True, f"Frequency: {freq_mhz} MHz")
            return self.feedback(False, f"Unexpected response: {response_str}")
        except Exception as e:
            return self.feedback(False, f"Error reading frequency: {e}")

    def write_frequency(self, ser, freq):
        """Set frequency (not directly supported on BCD325P2)."""
        return self.feedback(
            False, "Frequency input not supported via direct command."
        )

    def send_key(self, ser, keySeq):
        """Simulate key presses on the BCD325P2."""
        if not keySeq:
            return self.feedback(False, "No key(s) provided.")

        responses = []
        for char in keySeq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = self.send_command(ser, f"KEY,{char},P")
                response_str = self.ensure_str(
                    response
                )  # Convert bytes to string
                responses.append(f"{char} → {response_str}")
            except Exception as e:
                responses.append(f"{char} → ERROR: {e}")
        return "\n".join(responses)

    def dump_memory_to_file(
        self,
        ser,
        filename="memorydump.txt",
        start=0x00010000,
        end=0x0001FFFF,
        step=16,
    ):
        """Dump scanner memory to a file."""
        try:
            self.enter_programming_mode(ser)
            total_steps = ((end - start) // step) + 1
            valid_count, invalid_streak = 0, 0
            MAX_INVALID = 4096
            with open(filename, "w") as f:
                for i in range(total_steps):
                    addr = start + i * step
                    cmd = f"MRD,{hex32(addr)}"
                    response = self.send_command(ser, cmd)
                    response_str = self.ensure_str(
                        response
                    )  # Ensure we convert to string
                    if response_str.startswith("MRD,"):
                        f.write(response_str + "\n")
                        valid_count += 1
                        invalid_streak = 0
                    elif "ERR" in response_str or "NG" in response_str:
                        invalid_streak += 1
                    else:
                        f.write(f"# Unexpected: {response_str}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(
                            False, f"Aborted early — {MAX_INVALID} invalids."
                        )
                    update_progress(i, total_steps)
            self.exit_programming_mode(ser)
            return self.feedback(
                True, f"{valid_count} MRD entries written to {filename}"
            )
        except Exception as e:
            try:
                self.exit_programming_mode(ser)
            except Exception:  # Changed from bare except
                pass
            return self.feedback(False, f"Memory Dump Error: {e}")

    def read_global_lockout(self, ser):
        """Read global lockout frequencies."""
        try:
            self.enter_programming_mode(ser)
            results = []
            while True:
                response = self.send_command(
                    ser, self.commands["GLF"].buildCommand()
                )
                response_str = self.ensure_str(
                    response
                )  # Ensure we convert to string
                if response_str.strip() == "GLF,-1":
                    break
                results.append(response_str.strip())
            self.exit_programming_mode(ser)
            return "\n".join(results)
        except Exception as e:
            return self.feedback(False, f"Error reading global lockout: {e}")

    def read_channel_info(self, ser, index):
        """Read channel information."""
        try:
            self.enter_programming_mode(ser)
            response = self.send_command(ser, f"CIN,{index}")
            response_str = self.ensure_str(response)  # Convert bytes to string
            self.exit_programming_mode(ser)
            return response_str
        except Exception as e:
            return self.feedback(False, f"Error reading channel info: {e}")

    def write_channel_info(
        self, ser, index, name, freq_khz, mod, ctcss, delay, lockout, priority
    ):
        """Write channel information."""
        try:
            self.enter_programming_mode(ser)
            parts = [
                str(index),
                name[:16],
                str(freq_khz),
                mod.upper(),
                str(ctcss),
                str(delay),
                str(lockout),
                str(priority),
                "0",  # ATT
                "0",  # ALT
                "0",  # ALTL
                "",
                "",
                "",
                "",  # RSV
                "0",  # AUDIO_TYPE
                "0",  # P25NAC
                "0",  # NUMBER_TAG
                "OFF",  # ALT_COLOR
                "0",  # ALT_PATTERN
                "0",  # VOL_OFFSET
            ]
            response = self.send_command(ser, f"CIN,{','.join(parts)}")
            self.exit_programming_mode(ser)
            return self.feedback(
                "OK" in response, f"Channel {index} written → {response}"
            )
        except Exception as e:
            return self.feedback(False, f"Error writing channel info: {e}")

    def enter_quick_frequency_hold(self, ser, freq_mhz):
        """Enter frequency hold mode."""
        try:
            freq_str = f"{float(freq_mhz):08.5f}"
            freq_hecto_hertz = round(
                int(freq_mhz * 1_000_000 / 100)
            )  # Snake case for variable names too
            command = f"QSH,{freq_hecto_hertz}"
            response = self.send_command(ser, command)
            response_str = self.ensure_str(
                response
            )  # Ensure we convert to string
            if response_str.startswith("QSH,OK"):
                return self.feedback(
                    True, f"Entered frequency hold at {freq_str} MHz"
                )
            return self.feedback(
                False, f"Failed to enter frequency hold: {response_str}"
            )
        except Exception as e:
            return self.feedback(False, f"Error entering frequency hold: {e}")
