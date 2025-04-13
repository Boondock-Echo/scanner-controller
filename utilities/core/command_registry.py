"""
Command registry for REPL interface.

This module builds the command table and help text for the REPL interface.
"""

import logging
from typing import Callable, Dict, Tuple


def build_command_table(
    adapter, ser
) -> Tuple[Dict[str, Callable], Dict[str, str]]:
    """Build a command table and help text for the REPL interface."""
    commands = {}
    help_text = {}

    # Standard command mapping - ensure we're using snake_case method
    # names consistently
    command_map = {
        # Basic commands
        "read rssi": (
            "read_rssi",
            "Read the current signal strength (0.0-1.0)",
        ),
        "read volume": (
            "read_volume",
            "Read the current volume setting (0-29)",
        ),
        "read squelch": (
            "read_squelch",
            "Read the current squelch level (0-29)",
        ),
        "read frequency": ("read_frequency", "Read the current frequency"),
        "read status": ("read_status", "Read the scanner status"),
        "read battery": ("read_battery_voltage", "Read the battery voltage"),
        "read model": ("read_model", "Read the scanner model"),
        "read version": ("read_sw_ver", "Read the firmware version"),
        "read smeter": (
            "read_s_meter",
            "Read the S-meter value (if available)",
        ),
        # Control commands
        "write volume": (
            "write_volume",
            "Set the volume level (0-15). Example: write volume 10",
        ),
        "write squelch": (
            "write_squelch",
            "Set the squelch level (0-15). Example: write squelch 3",
        ),
        "write frequency": (
            "write_frequency",
            "Set the frequency in MHz. Example: write frequency 154.3",
        ),
        # Direct communication
        "send": (
            "send_command",
            "Send a raw command to the scanner. Example: send MDL",
        ),
        # Advanced features
        "keys": (
            "send_key",
            "Send key presses to the scanner. Example: keys 123",
        ),
        "hold": (
            "enter_quick_frequency_hold",
            "Enter frequency hold mode. Example: hold 154.3",
        ),
        "channel": (
            "read_channel_info",
            "Read channel information. Example: channel 10",
        ),
        "dump": (
            "dump_memory_to_file",
            "Dump scanner memory to a file. Example: dump memory.txt",
        ),
        "lockouts": ("read_global_lockout", "Read global lockout frequencies"),
        # Programming mode
        "prg": ("enter_programming_mode", "Enter programming mode"),
        "epg": ("exit_programming_mode", "Exit programming mode"),
    }

    # Build the command table and help text
    for cmd_name, (method_name, help_str) in command_map.items():
        if hasattr(adapter, method_name):
            # Create a closure to capture the method reference
            method = getattr(adapter, method_name)

            # For methods that require arguments, we wrap them to handle
            # arg parsing
            if method_name == "send_command":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(s, arg)
            elif method_name == "send_key":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(s, arg)
            elif method_name == "write_volume":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(s, int(arg))
            elif method_name == "write_squelch":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(s, int(arg))
            elif method_name == "write_frequency":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(
                    s, float(arg)
                )
            elif method_name == "enter_quick_frequency_hold":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(
                    s, float(arg)
                )
            elif method_name == "read_channel_info":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(s, int(arg))
            elif method_name == "dump_memory_to_file":
                commands[cmd_name] = lambda arg, m=method, s=ser: m(
                    s, arg or "memorydump.txt"
                )
            elif method_name in [
                "enter_programming_mode",
                "exit_programming_mode",
            ]:
                # These methods just need the serial port
                commands[cmd_name] = lambda arg="", m=method, s=ser: m(s)
            else:
                # For methods without arguments, we create a simple wrapper
                commands[cmd_name] = lambda arg="", m=method, s=ser: m(s)

            help_text[cmd_name] = help_str
        else:
            logging.debug(
                f"Method {method_name} not found in adapter,"
                f" skipping command {cmd_name}"
            )

    # Add aliases for common commands
    if "read rssi" in commands:
        commands["rssi"] = commands["read rssi"]
        help_text["rssi"] = help_text["read rssi"] + " (alias for 'read rssi')"

    if "read status" in commands:
        commands["status"] = commands["read status"]
        help_text["status"] = (
            help_text["read status"] + " (alias for 'read status')"
        )

    if "read frequency" in commands:
        commands["freq"] = commands["read frequency"]
        help_text["freq"] = (
            help_text["read frequency"] + " (alias for 'read frequency')"
        )

    if "read squelch" in commands:
        commands["squelch"] = commands["read squelch"]
        help_text["squelch"] = (
            help_text["read squelch"] + " (alias for 'read squelch')"
        )

    # Add adapter-specific info to help text
    model_name = (
        adapter.machine_mode_id
        if hasattr(adapter, "machine_mode_id")
        else "Unknown"
    )
    for cmd_name in help_text:
        help_text[cmd_name] = f"[{model_name}] {help_text[cmd_name]}"

    return commands, help_text
