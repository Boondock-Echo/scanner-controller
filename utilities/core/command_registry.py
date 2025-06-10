"""
Command Registry Module.

This module builds the command table from scanner adapter capabilities.
"""

import logging

from utilities.graph_utils import render_rssi_graph, render_band_scope_waterfall


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

    # -- Controlling Scanner commands --
    # Always register essential controlling scanner commands

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

    # Band scope (CSC streaming)
    if hasattr(adapter, 'stream_custom_search'):
        logging.debug("Registering 'band scope' command")

        def band_scope(ser_, adapter_, arg=""):
            parts = arg.split()
            count = int(parts[0]) if parts else 1024
            width = getattr(adapter_, "band_scope_width", 64) or 64
            pairs = []
            for rssi, freq, _ in adapter_.stream_custom_search(ser_, count):
                pairs.append(
                    (freq, rssi / 1023.0 if rssi is not None else None)
                )
            output = render_band_scope_waterfall(pairs, width)

            if width > 80:
                output = split_output_lines(output, 80)

            return output

        COMMANDS["band scope"] = band_scope
        COMMAND_HELP["band scope"] = (
            "Stream band scope data. Usage: band scope [record_count]"
        )
    else:
        logging.debug("Registering placeholder 'band scope' command")
        COMMANDS["band scope"] = lambda ser_, adapter_, arg="": (
            "Command 'band scope' not supported on this scanner model"
        )
        COMMAND_HELP["band scope"] = (
            "Stream band scope data. (Not available for this scanner model)"
        )

    # Band select presets
    if hasattr(adapter, 'configure_band_scope'):
        logging.debug("Registering 'band select' command")

        def band_select(ser_, adapter_, arg=""):
            parts = arg.split()
            return adapter_.configure_band_scope(ser_, *parts)

        COMMANDS["band select"] = band_select

        try:
            from config.band_scope_presets import BAND_SCOPE_PRESETS

            presets = ", ".join(sorted(BAND_SCOPE_PRESETS))
            preset_help = f" Available presets: {presets}"
        except ImportError:
            preset_help = ""

        COMMAND_HELP["band select"] = (
            f"Select a band using a preset. Usage: band select <preset> or "
            f"band select <low_freq> <high_freq> <step> <modulation>.{preset_help}"
        )
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
