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
from adapters.uniden.bcd325p2.close_call import (
    get_close_call,
    jump_mode,
    jump_to_number_tag,
    set_close_call,
)
from adapters.uniden.bcd325p2.frequency import (
    enter_quick_frequency_hold,
    read_frequency,
    write_frequency,
)
from adapters.uniden.bcd325p2.status_info import (
    read_battery_voltage,
    read_model,
    read_s_meter,
    read_status,
    read_sw_ver,
    read_window_voltage,
)
from adapters.uniden.bcd325p2.custom_search import stream_custom_search
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
    programming_session,
)

# First-party imports
from adapters.uniden.uniden_base_adapter import UnidenScannerAdapter

# Application imports
from command_libraries.uniden.bcd325p2_commands import commands
from config.step_size_defaults import STEP_SIZE_DEFAULTS
from utilities.validators import validate_enum

MOD_VALIDATOR = validate_enum("MOD", ["AM", "FM", "NFM", "WFM", "FMB", "AUTO"])

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
        self.last_center = None
        self.last_span = None
        self.last_step = None
        self.last_mod = None
        logger.info(
            f"BCD325P2 adapter initialized (machine_mode={machine_mode})"
        )
        logger.debug(f"Loaded {len(commands)} BCD325P2 commands")
        logger.debug(f"Machine mode ID: {self.machine_mode_id}")
        self.band_scope_width = None
        self.signal_bandwidth = None

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

    def read_rssi(self, ser):
        """Return the normalized RSSI using the ``PWR`` command."""
        try:
            response = self.send_command(ser, "PWR")
            response_str = ensure_str(response)
            parts = response_str.split(",")
            if len(parts) >= 2:
                return int(parts[1]) / 1023.0
        except Exception as e:
            logger.error(f"Error reading RSSI: {e}")
        return None

    def configure_band_scope(self, ser, *args):
        """Configure band scope system settings or apply a preset.

        Parameters
        ----------
        ser : serial.Serial
            Serial connection to the scanner.
        *args : tuple
            Either a single preset name or ``freq step span max_hold [bandwidth]`` values.

        Returns
        -------
        str
            Scanner feedback after sending the command or an error message.
        """
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

        allowed_spans = [
            0.2,
            0.4,
            0.6,
            0.8,
            1,
            2,
            4,
            6,
            8,
            10,
            20,
            40,
            60,
            80,
            100,
            120,
            140,
            160,
            180,
            200,
            250,
            300,
            350,
            400,
            450,
            500,
        ]
        # Select the smallest span value from the allowed_spans list that is greater than or equal to span_mhz.
        # If no such value exists, default to the largest value in the list.
        span_val = next((s for s in allowed_spans if s >= span_mhz), allowed_spans[-1])
        span = f"{span_val:g}M"
        max_hold = 0
        bandwidth = None

        self.last_center = center_khz / 1000.0
        self.last_span = span_val
        self.last_step = self._to_mhz(step)
        self.last_mod = mod

        response_value = None
        try:
            with programming_session(self, ser) as ok:
                if not ok:
                    return self.feedback(
                        False, "Failed to enter programming mode"
                    )

                cmd_obj = self.commands.get("BSP")
                if cmd_obj:
                    if cmd_obj.validator:
                        cmd_obj.validator([freq, step, span, max_hold])
                    cmd = cmd_obj.set_format.format(
                        freq=freq, step=step, span=span, max_hold=max_hold
                    )
                else:
                    cmd = f"BSP,{freq},{step},{span},{max_hold}"

                response = self.send_command(ser, cmd)
                response_str = ensure_str(response)
                self.band_scope_width = self._calc_band_scope_width(
                    span, bandwidth or step
                )
                self.signal_bandwidth = bandwidth
                response_value = self.feedback(True, response_str)
            # Start the band-scope search after exiting programming mode
            try:
                self.start_scanning(ser)
            except Exception as e:  # pragma: no cover - log and proceed
                logger.error(f"Error starting band scope search: {e}")
            return response_value
        except Exception as e:
            return self.feedback(False, f"Error configuring band scope: {e}")

    def _to_mhz(self, value):
        """Convert a numeric string with optional unit suffix to MHz."""
        value_str = str(value).strip().lower()

        if value_str.isdigit():
            ivalue = int(value_str)
            if ivalue > 10000:
                return ivalue / 10000.0
            return ivalue / 100000.0

        for suffix in ("mhz", "m"):
            if value_str.endswith(suffix):
                return float(value_str[: -len(suffix)])

        for suffix in ("khz", "k"):
            if value_str.endswith(suffix):
                return float(value_str[: -len(suffix)]) / 1000.0

        return float(value_str)

    def _to_khz(self, value):
        """Convert a numeric string with optional unit suffix to kHz."""
        value_str = str(value).strip().lower()

        if value_str.isdigit():
            ivalue = int(value_str)
            if ivalue > 10000:
                return ivalue / 10.0
            return ivalue / 100.0

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

    def sweep_band_scope(self, ser, center_freq, span, step, bandwidth=None):
        """Sweep across a frequency range and collect RSSI readings.

        Parameters
        ----------
        center_freq : str or float
            Center frequency (e.g. ``146``, ``146M`` or ``146000k``).
        span : str or float
            Span width of the sweep (e.g. ``2M`` or ``2000k``).
        step : str or float
            Step size between samples (e.g. ``0.5M`` or ``500k``).
        bandwidth : str or float, optional
            Signal bandwidth used to calculate display width.
        """
        try:
            center = self._to_mhz(center_freq)
            span_mhz = self._to_mhz(span)
            step_khz = self._to_khz(step)
            step_mhz = step_khz / 1000.0

            self.last_center = center
            self.last_span = span_mhz
            self.last_step = step_mhz
            self.last_mod = None

            start = center - span_mhz / 2.0
            end = center + span_mhz / 2.0

            results = []
            freq = start
            while freq <= end + 1e-6:
                self.write_frequency(ser, freq)
                rssi = self.read_rssi(ser)
                results.append((round(freq, 6), rssi))
                freq += step_mhz
            self.band_scope_width = self._calc_band_scope_width(
                span, bandwidth or step
            )
            self.signal_bandwidth = bandwidth
            return results
        except Exception as e:
            logger.error(f"Error sweeping band scope: {e}")
            return []

    # Channel methods
    read_channel_info = read_channel_info
    write_channel_info = write_channel_info
    read_global_lockout = read_global_lockout

    # Close Call methods
    get_close_call = get_close_call
    set_close_call = set_close_call
    jump_mode = jump_mode
    jump_to_number_tag = jump_to_number_tag

    # Custom search methods
    stream_custom_search = stream_custom_search

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
