"""
Uniden Base Adapter module.

This module provides functionality related to uniden base adapter.
"""

import logging

from adapters.base_adapter import BaseScannerAdapter


class UnidenScannerAdapter(BaseScannerAdapter):
    """Base adapter for Uniden scanners with Uniden-specific functionality.

    This class provides standardized implementations for Uniden scanners.
    All method names use snake_case to follow Python conventions.
    """

    def __init__(self, machine_mode=False, commands=None):
        """Initialize the Uniden scanner adapter."""
        super().__init__()
        self.machine_mode = machine_mode
        self.commands = commands or {}
        self.in_program_mode = False

    def ensure_bytes(self, data):
        """Convert to bytes if not already bytes."""
        if data is None:
            return b""
        if isinstance(data, str):
            return data.encode("ascii", errors="replace")
        return data

    def ensure_str(self, data):
        """Convert to string if not already a string."""
        if data is None:
            return ""
        if isinstance(data, bytes):
            return data.decode("ascii", errors="replace").strip()
        return str(data)

    def feedback(self, success, message):
        """Format feedback based on machine_mode setting."""
        if hasattr(self, "machine_mode") and self.machine_mode:
            status = "OK" if success else "ERROR"
            # Clean up the message for machine parsing
            msg = str(message).replace(" ", "_").replace(":", "_")
            return f"STATUS:{status}|MESSAGE:{msg}"
        return message

    def send_command(self, ser, cmd, delay=0.2):
        """Send a command to the scanner and get the response.

        Parameters
        ----------
        ser : serial.Serial
            Serial connection to the scanner.
        cmd : str or bytes
            Command to transmit.
        delay : float, optional
            Delay for the serial buffer clear before sending.  Defaults to
            ``0.2`` seconds.
        """
        try:
            from utilities.scanner.backend import (
                send_command as utils_send_command,
            )

            # Ensure command is a string
            if isinstance(cmd, bytes):
                cmd_str = cmd.decode("ascii", errors="replace")
            else:
                cmd_str = str(cmd)

            # Get the response using the utility function
            response = utils_send_command(ser, cmd_str, delay=delay)

            # Log the command and response
            logging.debug(
                f"Command: {cmd_str}, Response type: {type(response)}, "
                f"Value: {response!r}"
            )

            # Return bytes for consistency
            return self.ensure_bytes(response)
        except Exception as e:
            logging.error(f"Error in send_command: {e}")
            return b""

    def read_squelch(self, ser):
        """Read the squelch setting for Uniden scanners."""
        try:
            # Check if we have SQL in command registry
            if "SQL" in self.commands:
                cmd = self.commands["SQL"].build_command()
            else:
                # Direct string command if not in registry
                cmd = "SQL"

            response = self.send_command(ser, cmd)
            response_str = self.ensure_str(response)

            # Parse the response (format: "SQL,<level>")
            parts = response_str.split(",")
            if len(parts) >= 2 and parts[0] == "SQL":
                return int(parts[1])
            return 0
        except Exception as e:
            return self.feedback(False, f"Error reading squelch: {e}")

    def write_squelch(self, ser, value):
        """Set the squelch for Uniden scanners."""
        try:
            # Convert value to int in range 0-15
            level = int(max(0, min(15, value)))

            # Use command registry if available
            if "SQL" in self.commands:
                cmd = self.commands["SQL"].build_command(level)
            else:
                # Direct command otherwise
                cmd = f"SQL,{level}"

            response = self.send_command(ser, cmd)
            response_str = self.ensure_str(response)

            return "OK" in response_str
        except Exception as e:
            return self.feedback(False, f"Error setting squelch: {e}")

    def read_volume(self, ser):
        """Read the volume setting for Uniden scanners."""
        try:
            # Check if we have VOL in command registry
            if "VOL" in self.commands:
                cmd = self.commands["VOL"].build_command()
            else:
                # Direct string command if not in registry
                cmd = "VOL"

            response = self.send_command(ser, cmd)
            response_str = self.ensure_str(response)

            # Parse the response (format: "VOL,<level>")
            parts = response_str.split(",")
            if len(parts) >= 2 and parts[0] == "VOL":
                return int(parts[1])
            return 0
        except Exception as e:
            return self.feedback(False, f"Error reading volume: {e}")

    def write_volume(self, ser, value):
        """Set the volume for Uniden scanners."""
        try:
            # Convert value to int in range 0-15
            level = int(max(0, min(15, value)))

            # Use command registry if available
            if "VOL" in self.commands:
                cmd = self.commands["VOL"].build_command(level)
            else:
                # Direct command otherwise
                cmd = f"VOL,{level}"

            response = self.send_command(ser, cmd)
            response_str = self.ensure_str(response)

            return "OK" in response_str
        except Exception as e:
            return self.feedback(False, f"Error setting volume: {e}")

    def enter_programming_mode(self, ser):
        """Enter programming mode for Uniden scanners."""
        if hasattr(self, "in_program_mode") and self.in_program_mode:
            return "Already in programming mode"

        try:
            response = self.send_command(ser, "PRG")
            response_str = self.ensure_str(response)
            if "OK" in response_str:
                self.in_program_mode = True
                return "Entered programming mode"
            return f"Failed to enter programming mode: {response_str}"
        except Exception as e:
            return f"Error entering programming mode: {e}"

    def exit_programming_mode(self, ser):
        """Exit programming mode for Uniden scanners."""
        if not hasattr(self, "in_program_mode") or not self.in_program_mode:
            return "Not in programming mode"

        try:
            response = self.send_command(ser, "EPG")
            response_str = self.ensure_str(response)
            if "OK" in response_str:
                self.in_program_mode = False
                return "Exited programming mode"
            return f"Failed to exit programming mode: {response_str}"
        except Exception as e:
            return f"Error exiting programming mode: {e}"

    def read_model(self, ser):
        """Read the scanner model for Uniden scanners."""
        try:
            return self.send_command(ser, self.commands["MDL"].build_command())
        except Exception as e:
            return self.feedback(False, f"Error reading model: {e}")

    def read_sw_ver(self, ser):
        """Read the scanner firmware version for Uniden scanners."""
        try:
            return self.send_command(ser, self.commands["VER"].build_command())
        except Exception as e:
            return self.feedback(False, f"Error reading firmware version: {e}")
