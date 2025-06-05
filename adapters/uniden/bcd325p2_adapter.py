"""
BCD325P2 Scanner Adapter Module.

This module provides an adapter for the Uniden BCD325P2 scanner model, allowing
control and communication with the device through serial commands.
"""

# Standard library imports
import logging

# Import BCD325P2 specific functions
from adapters.uniden.bcd325p2.basic_io import (
    read_squelch,
    read_volume,
    write_squelch,
    write_volume,
)
from adapters.uniden.bcd325p2.channel import (
    read_channel_info,
    read_global_lockout,
    write_channel_info,
)
from adapters.uniden.bcd325p2.frequency import (
    enter_quick_frequency_hold,
    read_frequency,
    write_frequency,
)
from adapters.uniden.bcd325p2.close_call import (
    get_close_call,
    jump_mode,
    jump_to_number_tag,
    set_close_call,
)
from adapters.uniden.bcd325p2.status_info import (
    read_battery_voltage,
    read_model,
    read_s_meter,
    read_status,
    read_sw_ver,
    read_window_voltage,
)
from adapters.uniden.bcd325p2.user_control import (
    send_key,
    start_scanning,
    stop_scanning,
)

# Import common functions
from adapters.uniden.common.core import (
    ensure_bytes,
    ensure_str,
    feedback,
    send_command,
)
from adapters.uniden.common.programming import (
    enter_programming_mode,
    exit_programming_mode,
)

# First-party imports
from adapters.uniden.uniden_base_adapter import UnidenScannerAdapter

# Application imports
from command_libraries.uniden.bcd325p2_commands import commands

logger = logging.getLogger(__name__)


class BCD325P2Adapter(UnidenScannerAdapter):
    """Adapter for the BCD325P2 scanner."""

    def __init__(self, machine_mode=False):
        """Initialize the BCD325P2 adapter.

        Args:
            machine_mode: Whether to use machine-readable output format.
        """
        super().__init__(machine_mode, commands)
        self.machine_mode_id = "BCD325P2"
        self.in_program_mode = False
        logger.info(
            f"BCD325P2 adapter initialized (machine_mode={machine_mode})"
        )
        logger.debug(f"Loaded {len(commands)} BCD325P2 commands")
        logger.debug(f"Machine mode ID: {self.machine_mode_id}")

    # Import methods from modules
    # Core methods
    ensure_bytes = ensure_bytes
    ensure_str = ensure_str
    send_command = send_command

    def feedback(self, success, message):
        """Format feedback based on machine_mode setting."""
        return feedback(self.machine_mode, success, message)

    # Override programming mode methods to add logging
    def enter_programming_mode(self, ser):
        """Enter programming mode with logging."""
        logger.info("Attempting to enter programming mode")
        result = enter_programming_mode(self, ser)
        if result:
            logger.info("Successfully entered programming mode")
        else:
            logger.warning("Failed to enter programming mode")
        return result

    def exit_programming_mode(self, ser):
        """Exit programming mode with logging."""
        logger.info("Attempting to exit programming mode")
        result = exit_programming_mode(self, ser)
        if result:
            logger.info("Successfully exited programming mode")
        else:
            logger.warning("Failed to exit programming mode")
        return result

    # Basic I/O methods
    read_volume = read_volume
    write_volume = write_volume
    read_squelch = read_squelch
    write_squelch = write_squelch

    # Status and info methods
    read_model = read_model
    read_sw_ver = read_sw_ver
    read_s_meter = read_s_meter
    read_battery_voltage = read_battery_voltage
    read_window_voltage = read_window_voltage
    read_status = read_status

    # Frequency methods
    read_frequency = read_frequency
    write_frequency = write_frequency
    enter_quick_frequency_hold = enter_quick_frequency_hold

    # Channel methods
    read_channel_info = read_channel_info
    write_channel_info = write_channel_info
    read_global_lockout = read_global_lockout

    # Close Call methods
    get_close_call = get_close_call
    set_close_call = set_close_call
    jump_mode = jump_mode
    jump_to_number_tag = jump_to_number_tag

    # User control methods
    send_key = send_key
    start_scanning = start_scanning
    stop_scanning = stop_scanning

    def get_help(self, command):
        """Get help for a specific BCD325P2 command.

        Args:
            command: The command to get help for.

        Returns:
            str: Help text for the command.
        """
        try:
            logger.debug(f"Looking up help for command: {command}")
            cmd = self.commands.get(command.upper())
            if cmd and cmd.help:
                logger.debug(f"Found help for command: {command}")
                return self.feedback(True, cmd.help)
            logger.debug(f"No help found for command: {command}")
            return self.feedback(False, f"No help available for {command}")
        except Exception as e:
            logger.error(
                f"Error retrieving help for {command}: {e}", exc_info=True
            )
            return self.feedback(False, f"Error retrieving help: {e}")

    def __str__(self):
        """Return string representation of the adapter."""
        mode_str = "machine" if self.machine_mode else "human"
        prog_str = (
            "in programming mode"
            if self.in_program_mode
            else "not in programming mode"
        )
        return f"BCD325P2 Adapter ({mode_str} mode, {prog_str})"
