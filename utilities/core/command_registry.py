"""
Command Registry Module.

This module builds the command table from scanner adapter capabilities.
"""

import logging


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

    # Band scope configuration
    if hasattr(adapter, 'configure_band_scope'):
        logging.debug("Registering 'band scope' command")

        def band_scope(arg=""):
            parts = arg.split()
            return adapter.configure_band_scope(ser, *parts)

        COMMANDS["band scope"] = band_scope

        try:
            from config.band_scope_presets import BAND_SCOPE_PRESETS

            presets = ", ".join(sorted(BAND_SCOPE_PRESETS))
            preset_help = f" Available presets: {presets}"
        except ImportError:
            preset_help = ""

        COMMAND_HELP["band scope"] = (
            "Configure band scope settings. Usage: band scope <preset> or "
            "band scope <freq> <step> <span> <max_hold>." + preset_help
        )
    else:
        logging.debug("Registering placeholder 'band scope' command")
        COMMANDS["band scope"] = lambda arg: (
            "Command 'band scope' not supported on this scanner model"
        )
        COMMAND_HELP["band scope"] = (
            "Configure band scope settings. "
            "(Not available for this scanner model)"
        )

    # Band sweep
    if hasattr(adapter, 'sweep_band_scope'):
        logging.debug("Registering 'band sweep' command")

        def band_sweep(arg=""):
            parts = arg.split()
            return adapter.sweep_band_scope(ser, *parts)

        COMMANDS["band sweep"] = band_sweep
        COMMAND_HELP["band sweep"] = (
            "Sweep a range of frequencies. Usage: band sweep <center> <span> <step>"
        )
    else:
        logging.debug("Registering placeholder 'band sweep' command")
        COMMANDS["band sweep"] = lambda arg: (
            "Command 'band sweep' not supported on this scanner model"
        )
        COMMAND_HELP["band sweep"] = (
            "Sweep a range of frequencies. (Not available for this scanner model)"
        )

    # Custom search streaming
    if hasattr(adapter, 'run_custom_search'):
        logging.debug("Registering 'custom search' command")

        def custom_search(arg=""):
            try:
                count = int(arg) if arg else 50
            except ValueError:
                count = 50
            return adapter.run_custom_search(ser, max_results=count)

        COMMANDS["custom search"] = custom_search
        COMMAND_HELP["custom search"] = (
            "Run a custom search using CSC. Usage: custom search [max_results]"
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
