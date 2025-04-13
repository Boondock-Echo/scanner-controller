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
            return "OK" if success else "ERROR"
        return message

    def send_command(self, ser, cmd):
        """Send a command to the scanner and get the response."""
        try:
            from utilities.core.scanner_utils import send_command

            # Ensure command is a string before passing to underlying function
            if isinstance(cmd, bytes):
                cmd = cmd.decode("ascii", errors="replace")

            # Get the response (typically bytes)
            response = send_command(ser, cmd)

            # Log the command and response
            logging.debug(
                f"Command: {cmd}, Response type: {type(response)}, "
                f"Value: {response!r}"
            )

            # Make sure we return bytes for consistency
            return self.ensure_bytes(response)
        except Exception as e:
            logging.error(f"Error in send_command: {e}")
            return b""

    def read_squelch(self, ser):
        """Read the squelch setting for Uniden scanners."""
        try:
            # Check if we have SQL in command registry
            if "SQL" in self.commands:
                cmd = self.commands["SQL"].buildCommand()
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
                cmd = self.commands["SQL"].buildCommand(level)
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
                cmd = self.commands["VOL"].buildCommand()
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
                cmd = self.commands["VOL"].buildCommand(level)
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
        if self.in_program_mode:
            return "Already in programming mode"

        try:
            response = self.send_command(ser, "PRG")
            if "OK" in response:
                self.in_program_mode = True
                return "Entered programming mode"
            return f"Failed to enter programming mode: {response}"
        except Exception as e:
            return f"Error entering programming mode: {e}"

    def exit_programming_mode(self, ser):
        """Exit programming mode for Uniden scanners."""
        if not self.in_program_mode:
            return "Not in programming mode"

        try:
            response = self.send_command(ser, "EPG")
            if "OK" in response:
                self.in_program_mode = False
                return "Exited programming mode"
            return f"Failed to exit programming mode: {response}"
        except Exception as e:
            return f"Error exiting programming mode: {e}"

    def read_model(self, ser):
        """Read the scanner model for Uniden scanners."""
        try:
            return self.send_command(ser, self.commands["MDL"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading model: {e}")

    def read_sw_ver(self, ser):
        """Read the scanner firmware version for Uniden scanners."""
        try:
            return self.send_command(ser, self.commands["VER"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading firmware version: {e}")
