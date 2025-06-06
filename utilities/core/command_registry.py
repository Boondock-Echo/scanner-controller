"""
Command Registry Module.

This module builds the command table from scanner adapter capabilities.
"""

import logging

from utilities.graph_utils import (
    render_rssi_graph,
    render_band_scope_waterfall,
)


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
                lambda arg="", cmd=cmd_name: adapter.send_command(
                    ser, f"{cmd}{' ' + arg if arg else ''}"
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
    COMMANDS["send"] = lambda arg="": adapter.send_command(ser, arg)
    COMMAND_HELP["send"] = "Send a raw command to the scanner."

    # Register high-level commands based on adapter capabilities
    logging.info(
        "Registering high-level abstraction commands based on adapter "
        "capabilities"
    )

    # -- Volume commands --
    if hasattr(adapter, 'read_volume'):
        logging.debug("Registering 'get volume' command")
        COMMANDS["get volume"] = lambda: adapter.read_volume(ser)
        COMMAND_HELP["get volume"] = "Get the current volume level."

    if hasattr(adapter, 'write_volume'):
        logging.debug("Registering 'set volume' command")
        COMMANDS["set volume"] = lambda arg: adapter.write_volume(ser, arg)
        COMMAND_HELP["set volume"] = (
            "Set the volume level. Usage: set volume <level>"
        )

    # -- Squelch commands --
    if hasattr(adapter, 'read_squelch'):
        logging.debug("Registering 'get squelch' command")
        COMMANDS["get squelch"] = lambda: adapter.read_squelch(ser)
        COMMAND_HELP["get squelch"] = "Get the current squelch level."

    if hasattr(adapter, 'write_squelch'):
        logging.debug("Registering 'set squelch' command")
        COMMANDS["set squelch"] = lambda arg: adapter.write_squelch(ser, arg)
        COMMAND_HELP["set squelch"] = (
            "Set the squelch level. Usage: set squelch <level>"
        )

    # -- Additional commands based on adapter capabilities --
    # Battery voltage
    if hasattr(adapter, 'read_battery_voltage'):
        logging.debug("Registering 'get battery' command")
        COMMANDS["get battery"] = lambda: adapter.read_battery_voltage(ser)
        COMMAND_HELP["get battery"] = "Get the battery voltage."

    # Frequency
    if hasattr(adapter, 'read_frequency'):
        logging.debug("Registering 'get frequency' command")
        COMMANDS["get frequency"] = lambda: adapter.read_frequency(ser)
        COMMAND_HELP["get frequency"] = "Get the current frequency."

    if hasattr(adapter, 'write_frequency'):
        logging.debug("Registering 'set frequency' command")
        COMMANDS["set frequency"] = lambda arg: adapter.write_frequency(
            ser, arg
        )
        COMMAND_HELP["set frequency"] = (
            "Set the frequency. Usage: set frequency <freq_mhz>"
        )

    # Status
    if hasattr(adapter, 'read_status'):
        logging.debug("Registering 'get status' command")
        COMMANDS["get status"] = lambda: adapter.read_status(ser)
        COMMAND_HELP["get status"] = "Get the scanner status information."

    # Signal meter
    if hasattr(adapter, 'read_s_meter'):
        logging.debug("Registering 'get signal' command")
        COMMANDS["get signal"] = lambda: adapter.read_s_meter(ser)
        COMMAND_HELP["get signal"] = "Get the signal strength meter reading."

    # -- Controlling Scanner commands --
    # Always register essential controlling scanner commands

    # Send key
    if hasattr(adapter, 'send_key'):
        logging.debug("Registering 'send key' command")
        COMMANDS["send key"] = lambda arg: adapter.send_key(ser, arg)
        COMMAND_HELP["send key"] = (
            "Send key presses to the scanner. Usage: send key <sequence>"
        )
    else:
        logging.debug("Registering placeholder 'send key' command")
        COMMANDS["send key"] = lambda arg: (
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
            lambda arg: adapter.enter_quick_frequency_hold(ser, float(arg))
        )
        COMMAND_HELP["hold frequency"] = (
            "Enter frequency hold mode. Usage: hold frequency <freq_mhz>"
        )
    else:
        logging.debug("Registering placeholder 'hold frequency' command")
        COMMANDS["hold frequency"] = lambda arg: (
            "Command 'hold frequency' not supported on this scanner model"
        )
        COMMAND_HELP["hold frequency"] = (
            "Enter frequency hold mode. Usage: hold frequency <freq_mhz> "
            "(Not available for this scanner model)"
        )

    # Band scope (CSC streaming)
    if hasattr(adapter, 'stream_custom_search'):
        logging.debug("Registering 'band scope' command")

        def band_scope(arg=""):
            parts = arg.split()
            count = int(parts[0]) if parts else 1024
            if len(parts) > 1:
                width = int(parts[1])
            else:
                width = getattr(adapter, "band_scope_width", 64) or 64
            results = adapter.stream_custom_search(ser, count)
            pairs = [
                (freq, rssi / 1023.0 if rssi is not None else None)
                for rssi, freq, _ in results
            ]
            return render_band_scope_waterfall(pairs, width)

        COMMANDS["band scope"] = band_scope
        COMMAND_HELP["band scope"] = (
            "Stream band scope data. Usage: band scope [record_count] [width]"
        )
    else:
        logging.debug("Registering placeholder 'band scope' command")
        COMMANDS["band scope"] = lambda arg="": (
            "Command 'band scope' not supported on this scanner model"
        )
        COMMAND_HELP["band scope"] = (
            "Stream band scope data. (Not available for this scanner model)"
        )

    # Band sweep presets
    if hasattr(adapter, 'configure_band_scope'):
        logging.debug("Registering 'band sweep' command")

        def band_sweep(arg=""):
            parts = arg.split()
            return adapter.configure_band_scope(ser, *parts)

        COMMANDS["band sweep"] = band_sweep

        try:
            from config.band_scope_presets import BAND_SCOPE_PRESETS

            presets = ", ".join(sorted(BAND_SCOPE_PRESETS))
            preset_help = f" Available presets: {presets}"
        except ImportError:
            preset_help = ""

        COMMAND_HELP["band sweep"] = (
            "Sweep using a preset. Usage: band sweep <preset> or "
            "band sweep <freq> <step> <span> <max_hold>." + preset_help
        )
    else:
        logging.debug("Registering placeholder 'band sweep' command")
        COMMANDS["band sweep"] = lambda arg: (
            "Command 'band sweep' not supported on this scanner model"
        )
        COMMAND_HELP["band sweep"] = (
            "Sweep using a preset. (Not available for this scanner model)"
        )

    # Custom search (frequency sweep)
    if hasattr(adapter, 'sweep_band_scope'):
        logging.debug("Registering 'custom search' command")

        def custom_search(arg=""):
            parts = arg.split()
            return adapter.sweep_band_scope(ser, *parts)

        COMMANDS["custom search"] = custom_search
        COMMAND_HELP["custom search"] = (
            "Perform a custom frequency sweep. Usage: custom search "
            "<center> <span> <step>"
        )
    else:
        logging.debug("Registering placeholder 'custom search' command")
        COMMANDS["custom search"] = lambda arg: (
            "Command 'custom search' not supported on this scanner model"
        )
        COMMAND_HELP["custom search"] = (
            "Perform a custom frequency sweep. (Not available for this "
            "scanner model)"
        )

    # Dump memory
    if hasattr(adapter, 'dump_memory_to_file'):
        logging.debug("Registering 'dump memory' command")
        COMMANDS["dump memory"] = lambda: adapter.dump_memory_to_file(ser)
        COMMAND_HELP["dump memory"] = "Dump scanner memory to a file."
    else:
        logging.debug("Registering placeholder 'dump memory' command")
        COMMANDS["dump memory"] = (
            lambda: "Command 'dump memory' not supported on this scanner model"
        )
        COMMAND_HELP["dump memory"] = (
            "Dump scanner memory to a file. "
            "(Not available for this scanner model)"
        )

    # Close Call logging
    try:
        from utilities.scanner.close_call_logger import record_close_calls

        def _log_close_calls(arg="", lockout=False):
            band = arg.strip() or "air"
            return record_close_calls(adapter, ser, band, lockout=lockout)

        COMMANDS["log close calls"] = lambda arg="": _log_close_calls(arg)
        COMMAND_HELP[
            "log close calls"
        ] = "Log Close Call hits. Usage: log close calls <band>"

        COMMANDS["log close calls lockout"] = lambda arg="": _log_close_calls(
            arg, True
        )
        COMMAND_HELP[
            "log close calls lockout"
        ] = (
            "Log Close Call hits and lock them out. Usage: log close calls lockout <band>"
        )
    except Exception:
        logging.debug("Close Call logging utilities unavailable")

    # Scan start/stop
    if hasattr(adapter, 'start_scanning'):
        logging.debug("Registering 'scan start' command")
        COMMANDS["scan start"] = lambda: adapter.start_scanning(ser)
        COMMAND_HELP["scan start"] = "Start scanner scanning process."
    else:
        logging.debug("Registering placeholder 'scan start' command")
        COMMANDS["scan start"] = lambda: (
            "Command 'scan start' not supported on this scanner model"
        )
        COMMAND_HELP["scan start"] = (
            "Start scanner scanning process. "
            "(Not available for this scanner model)"
        )

    if hasattr(adapter, 'stop_scanning'):
        logging.debug("Registering 'scan stop' command")
        COMMANDS["scan stop"] = lambda: adapter.stop_scanning(ser)
        COMMAND_HELP["scan stop"] = "Stop scanner scanning process."
    else:
        logging.debug("Registering placeholder 'scan stop' command")
        COMMANDS["scan stop"] = lambda: (
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
