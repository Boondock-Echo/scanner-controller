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

    # Key simulation
    if hasattr(adapter, 'send_key'):
        logging.debug("Registering 'send key' command")
        COMMANDS["send key"] = lambda arg: adapter.send_key(ser, arg)
        COMMAND_HELP["send key"] = (
            "Send key presses to the scanner. Usage: send key <sequence>"
        )

    logging.info(
        f"Command table built successfully with {len(COMMANDS)} commands"
    )
    return COMMANDS, COMMAND_HELP
