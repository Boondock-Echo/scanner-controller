"""
BC125AT Scanner Adapter Module.

This module provides an adapter for the Uniden BC125AT scanner model, allowing
control and communication with the device through serial commands.
"""

# Standard library imports
import logging

from adapters.uniden.bc125at.advanced import dump_memory_to_file

# Import BC125AT specific functions
from adapters.uniden.bc125at.basic_io import (
    read_squelch,
    read_volume,
    write_squelch,
    write_volume,
)
from adapters.uniden.bc125at.channel import (
    read_channel_info,
    read_global_lockout,
    write_channel_info,
)
from adapters.uniden.bc125at.frequency import (
    enter_quick_frequency_hold,
    read_frequency,
    write_frequency,
)
from adapters.uniden.bc125at.status_info import (
    read_battery_voltage,
    read_model,
    read_rssi,
    read_s_meter,
    read_status,
    read_sw_ver,
    read_window_voltage,
)
from adapters.uniden.bc125at.user_control import send_key

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
    programming_session,
)

# First-party imports
from adapters.uniden.uniden_base_adapter import (
    UnidenScannerAdapter,  # Correct import path
)

# Local imports
from command_libraries.uniden.bc125at_commands import commands
from config.step_size_defaults import STEP_SIZE_DEFAULTS
from utilities.validators import validate_enum

MOD_VALIDATOR = validate_enum("MOD", ["AM", "FM", "NFM", "WFM", "FMB", "AUTO"])

logger = logging.getLogger(__name__)


class BC125ATAdapter(UnidenScannerAdapter):
    """Adapter for the BC125AT scanner."""

    def __init__(self, machine_mode=False):
        """Initialize the BC125AT adapter.

        Args:
            machine_mode: Whether to use machine-readable output format.
        """
        super().__init__(machine_mode, commands)
        self.machine_mode_id = "BC125AT"
        self.in_program_mode = False
        self.band_scope_width = None
        self.signal_bandwidth = None
        logger.info(
            f"BC125AT adapter initialized (machine_mode={machine_mode})"
        )
        logger.debug(f"Loaded {len(commands)} BC125AT commands")
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
    read_rssi = read_rssi
    read_battery_voltage = read_battery_voltage
    read_window_voltage = read_window_voltage
    read_status = read_status
    read_s_meter = read_s_meter

    # Frequency methods
    read_frequency = read_frequency
    write_frequency = write_frequency
    enter_quick_frequency_hold = enter_quick_frequency_hold

    # Channel methods
    read_channel_info = read_channel_info
    write_channel_info = write_channel_info
    read_global_lockout = read_global_lockout

    # Advanced methods
    dump_memory_to_file = dump_memory_to_file

    # User control methods
    send_key = send_key

    def _to_mhz(self, value):
        """Convert a value with optional unit suffix to MHz."""
        value_str = str(value).strip().lower()
        for suffix in ("mhz", "m"):
            if value_str.endswith(suffix):
                return float(value_str[: -len(suffix)])
        for suffix in ("khz", "k"):
            if value_str.endswith(suffix):
                return float(value_str[: -len(suffix)]) / 1000.0
        return float(value_str)

    def _to_khz(self, value):
        """Convert a value with optional unit suffix to kHz."""
        value_str = str(value).strip().lower()
        for suffix in ("khz", "k"):
            if value_str.endswith(suffix):
                return float(value_str[: -len(suffix)])
        for suffix in ("mhz", "m"):
            if value_str.endswith(suffix):
                return float(value_str[: -len(suffix)]) * 1000.0
        return float(value_str)

    def _calc_band_scope_width(self, span, bandwidth):
        """Return the number of sweep bins from span and bandwidth values.

        Bare integers are interpreted as hundredths of a kilohertz
        (e.g. ``833`` becomes ``8.33 kHz``).
        """
        try:
            span_mhz = self._to_mhz(span)
            bw_val = str(bandwidth).strip().lower()
            if any(bw_val.endswith(s) for s in ("mhz", "m", "khz", "k")):
                bw_mhz = self._to_mhz(bandwidth)
            else:
                if bw_val.lstrip("-+").isdigit():
                    bw_khz = float(bw_val) / 100.0
                else:
                    bw_khz = float(bw_val)
                bw_mhz = bw_khz / 1000.0
            if bw_mhz <= 0:
                return None
            width = int(round(span_mhz / bw_mhz)) + 1
            return max(width, 1)
        except Exception:
            return None

    def configure_band_scope(self, ser, *args):
        """Configure and sweep a band using preset or parameters."""
        if not args:
            return self.feedback(
                False,
                "Expected a preset name or <low_freq> <high_freq> <step> <modulation>",
            )

        band = None
        if len(args) == 1:
            band = str(args[0]).lower()
            try:
                from config.band_scope_presets import BAND_SCOPE_PRESETS

                if band not in BAND_SCOPE_PRESETS:
                    return self.feedback(False, f"Unknown preset '{band}'")

                low, high, step, mod = BAND_SCOPE_PRESETS[band]
            except Exception as e:
                return self.feedback(False, f"Error loading presets: {e}")
        elif len(args) == 4:
            low, high, step, mod = args
        elif len(args) == 3:
            band = str(args[0]).lower()
            low, high, mod = args
            step = STEP_SIZE_DEFAULTS.get(band)
        else:
            return self.feedback(
                False,
                "Expected a preset name or <low_freq> <high_freq> [step] <modulation>",
            )

        if step in (None, ""):
            if band and band in STEP_SIZE_DEFAULTS:
                step = STEP_SIZE_DEFAULTS[band]
        try:
            MOD_VALIDATOR(mod)
        except ValueError as e:
            return self.feedback(False, str(e))

        low_khz = self._to_khz(low)
        high_khz = self._to_khz(high)
        span_mhz = (high_khz - low_khz) / 1000.0
        center_khz = (low_khz + high_khz) / 2.0
        freq = f"{int(round(center_khz * 10)):08d}"
        span = f"{span_mhz:g}M"

        with programming_session(self, ser) as ok:
            if not ok:
                return self.feedback(False, "Failed to enter programming mode")
            return self.sweep_band_scope(ser, freq, span, step)

    def sweep_band_scope(self, ser, center_freq, span, step, bandwidth=None):
        """Sweep across a frequency range using quick hold mode."""
        try:
            center = self._to_mhz(center_freq)
            span_mhz = self._to_mhz(span)
            step_khz = self._to_khz(step)
            step_mhz = step_khz / 1000.0

            start = center - span_mhz / 2.0
            end = center + span_mhz / 2.0

            results = []
            freq = start
            while freq <= end + 1e-6:
                self.enter_quick_frequency_hold(ser, freq)
                rssi_val = self.read_rssi(ser)
                try:
                    if isinstance(rssi_val, str) and "RSSI" in rssi_val:
                        rssi_val = float(rssi_val.split("RSSI")[-1].split()[0])
                except Exception:
                    rssi_val = None
                results.append((round(freq, 6), rssi_val))
                freq += step_mhz
            self.band_scope_width = self._calc_band_scope_width(
                span, bandwidth or step
            )
            self.signal_bandwidth = bandwidth
            return results
        except Exception as e:
            logger.error(f"Error sweeping band scope: {e}")
            return []

    def get_help(self, command):
        """Get help for a specific BC125AT command.

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
        return f"BC125AT Adapter ({mode_str} mode, {prog_str})"
