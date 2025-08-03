"""
Command Registry Module.

This module builds the command table from scanner adapter capabilities.
"""

import itertools
import logging
import sys
import config

# Maximum RSSI value returned by scanners
MAX_RSSI = 1023.0

from utilities.graph_utils import render_rssi_graph


def build_command_table(adapter, ser):
    """
    Build command table from adapter.

    Args:
        adapter: Scanner adapter instance
        ser: Serial connection to scanner

    Returns:
        tuple: (commands_dict, help_dict)
    """
    COMMANDS = {}
    COMMAND_HELP = {}

    logging.info(
        f"Building command table for adapter: {adapter.__class__.__name__}"
    )

    # Add device-specific commands from adapter's command registry
    if hasattr(adapter, 'commands'):
        logging.debug(f"Found {len(adapter.commands)} device-specific commands")
        for cmd_name, cmd_obj in adapter.commands.items():
            cmd_lower = cmd_name.lower()

            # Log each command as it's being registered
            logging.debug(f"Registering device command: {cmd_name}")

            # Create the command handler function
            COMMANDS[cmd_lower] = (
                lambda ser_, adapter_, arg="", cmd=cmd_name: adapter_.send_command(
                    ser_, f"{cmd}{' ' + arg if arg else ''}"
                )
            )

            # Add help text if available
            if hasattr(cmd_obj, 'help') and cmd_obj.help:
                COMMAND_HELP[cmd_lower] = cmd_obj.help.strip()
                logging.debug(f"Added help text for: {cmd_name}")
    else:
        logging.warning(
            "Adapter has no commands attribute - no device-specific commands "
            "registered"
        )

    # Add standard "send" command for direct command sending
    logging.debug("Registering 'send' command for raw command transmission")
    COMMANDS["send"] = lambda ser_, adapter_, arg="": adapter_.send_command(
        ser_, arg
    )
    COMMAND_HELP["send"] = "Send a raw command to the scanner."

    # Register high-level commands based on adapter capabilities
    logging.info(
        "Registering high-level abstraction commands based on adapter "
        "capabilities"
    )

    # -- Volume commands --
    if hasattr(adapter, 'read_volume'):
        logging.debug("Registering 'get volume' command")
        COMMANDS["get volume"] = lambda ser_, adapter_: adapter_.read_volume(
            ser_
        )
        COMMAND_HELP["get volume"] = "Get the current volume level."

    if hasattr(adapter, 'write_volume'):
        logging.debug("Registering 'set volume' command")
        COMMANDS["set volume"] = (
            lambda ser_, adapter_, arg: adapter_.write_volume(ser_, arg)
        )
        COMMAND_HELP["set volume"] = (
            "Set the volume level. Usage: set volume <level>"
        )

    # -- Squelch commands --
    if hasattr(adapter, 'read_squelch'):
        logging.debug("Registering 'get squelch' command")
        COMMANDS["get squelch"] = lambda ser_, adapter_: adapter_.read_squelch(
            ser_
        )
        COMMAND_HELP["get squelch"] = "Get the current squelch level."

    if hasattr(adapter, 'write_squelch'):
        logging.debug("Registering 'set squelch' command")
        COMMANDS["set squelch"] = (
            lambda ser_, adapter_, arg: adapter_.write_squelch(ser_, arg)
        )
        COMMAND_HELP["set squelch"] = (
            "Set the squelch level. Usage: set squelch <level>"
        )

    # -- Additional commands based on adapter capabilities --
    # Battery voltage
    if hasattr(adapter, 'read_battery_voltage'):
        logging.debug("Registering 'get battery' command")
        COMMANDS["get battery"] = (
            lambda ser_, adapter_: adapter_.read_battery_voltage(ser_)
        )
        COMMAND_HELP["get battery"] = "Get the battery voltage."

    # Frequency
    if hasattr(adapter, 'read_frequency'):
        logging.debug("Registering 'get frequency' command")
        COMMANDS["get frequency"] = (
            lambda ser_, adapter_: adapter_.read_frequency(ser_)
        )
        COMMAND_HELP["get frequency"] = "Get the current frequency."

    if hasattr(adapter, 'write_frequency'):
        logging.debug("Registering 'set frequency' command")
        COMMANDS["set frequency"] = (
            lambda ser_, adapter_, arg: adapter_.write_frequency(ser_, arg)
        )
        COMMAND_HELP["set frequency"] = (
            "Set the frequency. Usage: set frequency <freq_mhz>"
        )

    # Status
    if hasattr(adapter, 'read_status'):
        logging.debug("Registering 'get status' command")
        COMMANDS["get status"] = lambda ser_, adapter_: adapter_.read_status(
            ser_
        )
        COMMAND_HELP["get status"] = "Get the scanner status information."

    # Signal meter
    if hasattr(adapter, 'read_s_meter'):
        logging.debug("Registering 'get signal' command")
        COMMANDS["get signal"] = lambda ser_, adapter_: adapter_.read_s_meter(
            ser_
        )
        COMMAND_HELP["get signal"] = "Get the signal strength meter reading."

    # -- Scanner Control commands --
    # Always register essential scanner control commands

    # Send key
    if hasattr(adapter, 'send_key'):
        logging.debug("Registering 'send key' command")
        COMMANDS["send key"] = lambda ser_, adapter_, arg: adapter_.send_key(
            ser_, arg
        )
        COMMAND_HELP["send key"] = (
            "Send key presses to the scanner. Usage: send key <sequence>"
        )
    else:
        logging.debug("Registering placeholder 'send key' command")
        COMMANDS["send key"] = lambda ser_, adapter_, arg: (
            "Command 'send key' not supported on this scanner model"
        )
        COMMAND_HELP["send key"] = (
            "Send key presses to the scanner. Usage: send key <sequence> "
            "(Not available for this scanner model)"
        )

    # Hold frequency
    if hasattr(adapter, 'enter_quick_frequency_hold'):
        logging.debug("Registering 'hold frequency' command")
        COMMANDS["hold frequency"] = (
            lambda ser_, adapter_, arg: adapter_.enter_quick_frequency_hold(
                ser_, float(arg)
            )
        )
        COMMAND_HELP["hold frequency"] = (
            "Enter frequency hold mode. Usage: hold frequency <freq_mhz>"
        )
    else:
        logging.debug("Registering placeholder 'hold frequency' command")
        COMMANDS["hold frequency"] = lambda ser_, adapter_, arg: (
            "Command 'hold frequency' not supported on this scanner model"
        )
        COMMAND_HELP["hold frequency"] = (
            "Enter frequency hold mode. Usage: hold frequency <freq_mhz> "
            "(Not available for this scanner model)"
        )

    # Band scope (CSC streaming or search sweep)
    if hasattr(adapter, 'stream_custom_search') or hasattr(adapter, 'search_band_scope'):
        logging.debug("Registering 'band scope' command")

        def band_scope(ser_, adapter_, arg=""):
            parts = arg.split()
            sweep_count = 1
            mode = "list"
            preset = None
            use_search_sweep = False

            # Handle Close Call subcommands: "band scope <preset> cc search|log"
            if len(parts) >= 2 and parts[1].lower() == "cc":
                preset = parts[0].lower()
                action = parts[2].lower() if len(parts) >= 3 else ""
                if action == "search":
                    try:
                        from utilities.scanner.close_call_search import (
                            close_call_search,
                        )

                        # Allow the user to terminate the search by pressing
                        # Enter or ``q``. The adapter's previous settings are
                        # restored automatically.
                        hits, _ = close_call_search(
                            adapter_, ser_, preset, input_stream=sys.stdin
                        )
                        return "\n".join(
                            f"{freq:.4f}"
                            for _, freq, _, _ in hits
                            if freq is not None
                        )
                    except Exception as exc:  # pragma: no cover - best effort
                        return str(exc)
                if action == "log":
                    try:
                        from utilities.scanner.close_call_logger import (
                            record_close_calls,
                        )

                        return record_close_calls(adapter_, ser_, preset)
                    except Exception as exc:  # pragma: no cover - best effort
                        return str(exc)
                return "Usage: band scope <preset> cc search|log"

            # Determine first non-flag token for preset or sweep count
            first_non_flag_found = False
            for part in parts:
                lower = part.lower()
                if lower in ("list", "hits"):
                    mode = lower
                    continue
                if lower == "search":
                    use_search_sweep = True
                    continue
                if not first_non_flag_found:
                    first_non_flag_found = True
                    try:
                        from config.band_scope_presets import BAND_SCOPE_PRESETS

                        if lower in BAND_SCOPE_PRESETS:
                            preset = lower
                            continue
                    except Exception:
                        pass
                    try:
                        sweep_count = int(part)
                    except ValueError:
                        pass
                else:
                    try:
                        sweep_count = int(part)
                    except ValueError:
                        pass

            records = []

            if use_search_sweep:
                if not hasattr(adapter_, "search_band_scope"):
                    return "Search-based sweep not supported on this scanner"
                if not preset:
                    return "Usage: band scope <preset> search"
                for _ in range(sweep_count):
                    sweep_records = adapter_.search_band_scope(ser_, preset)
                    records.extend(sweep_records)
                if not records:
                    return "No band scope data received"
            else:
                if preset and hasattr(adapter_, "configure_band_scope"):
                    result = adapter_.configure_band_scope(ser_, preset)
                    if result and "OK" not in result.upper():
                        return result

                if getattr(adapter_, "in_program_mode", False):
                    return (
                        "Scanner is in programming mode. "
                        "Run 'send EPG' then rerun 'band scope'."
                    )

                width = getattr(adapter_, "band_scope_width", None) or 1024
                record_count = width * sweep_count

                debug_mode = logging.getLogger().isEnabledFor(logging.DEBUG)
                show_progress = sys.stdout.isatty()
                spinner = itertools.cycle("|/-\\") if show_progress else None
                processed = 0
                for rssi, freq, _ in adapter_.stream_custom_search(
                    ser_, record_count, debug=debug_mode
                ):
                    records.append((rssi, freq))
                    if show_progress:
                        processed += 1
                        ch = next(spinner)
                        percent = processed / record_count * 100
                        sys.stdout.write(f"\r{ch} {percent:5.1f}%")
                        sys.stdout.flush()
                if show_progress:
                    sys.stdout.write("\r")
                    sys.stdout.flush()

                if not records:
                    return "No band scope data received"

            freqs = [f for _, f in records]
            if freqs:
                f_min = min(freqs)
                f_max = max(freqs)
            else:
                center = getattr(adapter_, "last_center", None)
                span = getattr(adapter_, "last_span", None)
                if center is not None and span is not None:
                    f_min = center - span / 2.0
                    f_max = center + span / 2.0
                else:
                    f_min = f_max = None

            center = getattr(adapter_, "last_center", None)
            span = getattr(adapter_, "last_span", None)
            step = getattr(adapter_, "last_step", None)
            mod = getattr(adapter_, "last_mod", None)

            if center is None and f_min is not None and f_max is not None:
                center = (f_min + f_max) / 2.0
            if span is None and f_min is not None and f_max is not None:
                span = f_max - f_min

            def fmt_freq(val):
                return f"{val:.3f}" if val is not None else "n/a"

            def fmt_span(val):
                if val is None:
                    return "n/a"
                if val >= 1:
                    return f"{val:g}M"
                return f"{val * 1000:g}k"

            summary = (
                f"center={fmt_freq(center)} min={fmt_freq(f_min)} "
                f"max={fmt_freq(f_max)} span={fmt_span(span)} "
                f"step={fmt_span(step)} mod={mod or 'N/A'}"
            )

            lines = []
            if mode == "hits":
                rssi_vals = [(r or 0) for r, _ in records]
                mean_rssi = sum(rssi_vals) / len(records)
                threshold = mean_rssi * 1.2
                for rssi, freq in records:
                    if rssi is None or freq is None:
                        continue
                    if rssi > threshold:
                        lines.append(f"{freq:.4f}, {rssi / MAX_RSSI:.3f}")
            else:
                for rssi, freq in records:
                    if rssi is None or freq is None:
                        continue
                    lines.append(f"{freq:.4f}, {rssi / MAX_RSSI:.3f}")

            return "\n".join(lines + [summary])

        COMMANDS["band scope"] = band_scope
        COMMAND_HELP["band scope"] = (
            "Stream band scope data or manage Close Call. Usage: band scope <preset> "
            "[sweeps] [list|hits] [search] | band scope <preset> cc search|log. "
            "During 'cc search', press Enter or 'q' to stop. "
            "Append 'search' to use a PWR-based sweep on models without CSC streaming."
        )

        logging.debug("Registering 'band sweep' command")

        def band_sweep(ser_, adapter_, arg=""):
            parts = arg.split()
            count = int(parts[0]) if parts else 1024
            output_lines = []
            debug_mode = logging.getLogger().isEnabledFor(logging.DEBUG)
            for rssi, freq, _ in adapter_.stream_custom_search(
                ser_, count, debug=debug_mode
            ):
                if rssi is None or freq is None:
                    continue
                output_lines.append(f"{freq:.4f}, {rssi / MAX_RSSI:.3f}")
            return "\n".join(output_lines)
        COMMANDS["band sweep"] = band_sweep
        COMMAND_HELP["band sweep"] = (
            "Stream band sweep data. Usage: band sweep [record_count]"
        )
    else:
        logging.debug("Registering placeholder 'band scope' command")
        COMMANDS["band scope"] = lambda ser_, adapter_, arg="": (
            "Command 'band scope' not supported on this scanner model"
        )
        COMMAND_HELP["band scope"] = (
            "Stream band scope data or manage Close Call. (Not available for this scanner model)"
        )

    # Band select presets
    if hasattr(adapter, 'configure_band_scope'):
        logging.debug("Registering 'band select' command")

        def band_select(ser_, adapter_, arg=""):
            parts = arg.split()
            return adapter_.configure_band_scope(ser_, *parts)

        COMMANDS["band select"] = band_select
        COMMANDS["band set"] = band_select

        try:
            from config.band_scope_presets import BAND_SCOPE_PRESETS

            presets = ", ".join(sorted(BAND_SCOPE_PRESETS))
            preset_help = f" Available presets: {presets}"
        except ImportError:
            preset_help = ""

        help_msg = (
            f"Select a band using a preset. Usage: band select <preset> or "
            f"band select <low_freq> <high_freq> <step> <modulation>.{preset_help}"
        )
        COMMAND_HELP["band select"] = help_msg
        COMMAND_HELP["band set"] = help_msg
    else:
        logging.debug("Registering placeholder 'band select' command")
        COMMANDS["band select"] = lambda ser_, adapter_, arg: (
            "Command 'band select' not supported on this scanner model"
        )
        COMMAND_HELP["band select"] = (
            "Select a band using a preset. (Not available for this scanner model)"
        )

    # Custom search (frequency sweep)
    if hasattr(adapter, 'sweep_band_scope'):
        logging.debug("Registering 'custom search' command")

        def custom_search(ser_, adapter_, arg=""):
            parts = arg.split()
            return adapter_.sweep_band_scope(ser_, *parts)

        COMMANDS["custom search"] = custom_search
        COMMAND_HELP["custom search"] = (
            "Perform a custom frequency sweep. Usage: custom search "
            "<center> <span> <step> [bandwidth]"
        )
    else:
        logging.debug("Registering placeholder 'custom search' command")
        COMMANDS["custom search"] = lambda ser_, adapter_, arg: (
            "Command 'custom search' not supported on this scanner model"
        )
        COMMAND_HELP["custom search"] = (
            "Perform a custom frequency sweep. (Not available for this "
            "scanner model)"
        )

    # Dump memory
    if hasattr(adapter, 'dump_memory_to_file'):
        logging.debug("Registering 'dump memory' command")
        COMMANDS["dump memory"] = (
            lambda ser_, adapter_: adapter_.dump_memory_to_file(ser_)
        )
        COMMAND_HELP["dump memory"] = "Dump scanner memory to a file."
    else:
        logging.debug("Registering placeholder 'dump memory' command")
        COMMANDS["dump memory"] = (
            lambda ser_, adapter_: "Command 'dump memory' not supported on this scanner model"
        )
        COMMAND_HELP["dump memory"] = (
            "Dump scanner memory to a file. "
            "(Not available for this scanner model)"
        )

    # Close Call logging
    try:
        from utilities.scanner.close_call_logger import record_close_calls

        def _log_close_calls(ser_, adapter_, arg="", lockout=False):
            band = arg.strip() or "air"
            return record_close_calls(adapter_, ser_, band, lockout=lockout)

        COMMANDS["log close calls"] = (
            lambda ser_, adapter_, arg="": _log_close_calls(ser_, adapter_, arg)
        )
        COMMAND_HELP["log close calls"] = (
            "Log Close Call hits. Usage: log close calls <band>"
        )

        COMMANDS["log close calls lockout"] = (
            lambda ser_, adapter_, arg="": _log_close_calls(
                ser_, adapter_, arg, True
            )
        )
        COMMAND_HELP["log close calls lockout"] = (
            "Log Close Call hits and lock them out. Usage: log close calls lockout <band>"
        )
    except Exception:
        logging.debug("Close Call logging utilities unavailable")

    # Scan start/stop
    if hasattr(adapter, 'start_scanning'):
        logging.debug("Registering 'scan start' command")
        COMMANDS["scan start"] = lambda ser_, adapter_: adapter_.start_scanning(
            ser_
        )
        COMMAND_HELP["scan start"] = "Start scanner scanning process."
    else:
        logging.debug("Registering placeholder 'scan start' command")
        COMMANDS["scan start"] = lambda ser_, adapter_: (
            "Command 'scan start' not supported on this scanner model"
        )
        COMMAND_HELP["scan start"] = (
            "Start scanner scanning process. "
            "(Not available for this scanner model)"
        )

    if hasattr(adapter, 'stop_scanning'):
        logging.debug("Registering 'scan stop' command")
        COMMANDS["scan stop"] = lambda ser_, adapter_: adapter_.stop_scanning(
            ser_
        )
        COMMAND_HELP["scan stop"] = "Stop scanner scanning process."
    else:
        logging.debug("Registering placeholder 'scan stop' command")
        COMMANDS["scan stop"] = lambda ser_, adapter_: (
            "Command 'scan stop' not supported on this scanner model"
        )
        COMMAND_HELP["scan stop"] = (
            "Stop scanner scanning process. "
            "(Not available for this scanner model)"
        )

    logging.info(
        f"Command table built successfully with {len(COMMANDS)} commands"
    )
    return COMMANDS, COMMAND_HELP
