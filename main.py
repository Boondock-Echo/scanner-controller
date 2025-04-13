"""
Main module.

This module provides functionality related to main.
"""

# Standard library imports
import argparse

# Third-party imports
import importlib
import json
import logging
import os
import re
import sys
import threading
from pathlib import Path

import serial

# Application imports
from utilities.core.command_registry import build_command_table
from utilities.core.scanner_utils import find_all_scanner_ports
from utilities.core.shared_utils import diagnose_connection_issues
from utilities.help_topics import get_extended_help
from utilities.log_trim import trim_log_file
from utilities.readlineSetup import initialize_readline
from utilities.scanner_factory import get_scanner_adapter

# ------------------------------------------------------------------------------
# LOGGING SETUP
# ------------------------------------------------------------------------------


def setup_logging(log_level=logging.DEBUG):
    """
    Set up logging configuration with the specified log level.

    Configures handlers, formatters and other logging settings based on the
    specified level.
    """
    logging.basicConfig(
        filename="scanner_tool.log",
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not os.path.exists("scanner_tool.log"):
        logging.error("Log file not found. Creating a new one.")

    if os.path.getsize("scanner_tool.log") > 10 * 1024 * 1024:  # 10 MB limit
        logging.info("Log file size exceeded 10 MB. Trimming...")
        trim_log_file(
            "scanner_tool.log", max_size=10 * 1024 * 1024
        )  # Keep the log file manageable


setup_logging()

# ------------------------------------------------------------------------------
# SUPPORTED SCANNER ADAPTERS
# ------------------------------------------------------------------------------

# Maps scanner model names to their respective adapter classes
adapter_scanner = {  # if your scanner adapter is not listed here, add it here
    """
    get adapter function.

    Provides functionality for get adapter.
    """
    "BC125AT": "adapters.uniden.bc125at_adapter.BC125ATAdapter",
    "BCD325P2": "adapters.uniden.bcd325p2_adapter.BCD325P2Adapter",
}


# Helper function to load the adapter
def get_adapter(model_name):
    """
    Load the adapter for the given scanner model.

    Parameters:
        model_name (str): The name of the scanner model.

    Returns:
        object: The adapter instance for the scanner model.

    Raises:
        ValueError: If the scanner model is unsupported.
        ImportError: If there is an error loading the adapter.
    """
    if model_name not in adapter_scanner:
        raise ValueError(f"Unsupported scanner model: {model_name}")

    try:
        module_path, class_name = adapter_scanner[model_name].rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)()
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Error loading adapter for {model_name}: {e}")


# ------------------------------------------------------------------------------
# HELP COMMAND
# ------------------------------------------------------------------------------
def show_help(COMMANDS, COMMAND_HELP, command="", adapter=None):
    """
    Display help for a command or list all available commands.

    Parameters:
        COMMANDS (dict): Dictionary of available commands.
        COMMAND_HELP (dict): Dictionary of help texts for commands.
        command (str): Specific command to display help for.
        adapter (object): Scanner adapter instance.
    """
    if not command:
        categories = {
            "Reading Information": [
                "read",
                "status",
                "rssi",
                "freq",
                "squelch",
            ],
            "Controlling Scanner": ["write", "hold", "keys"],
            "Programming": ["channel", "prg", "epg", "dump", "lockouts"],
            "Other": ["send", "help"],
        }

        print("\nAvailable commands:")
        available_cmds = sorted(COMMANDS.keys())

        for category, prefixes in categories.items():
            matching_cmds = []
            for prefix in prefixes:
                matching_cmds.extend(
                    [cmd for cmd in available_cmds if cmd.startswith(prefix)]
                )

            if matching_cmds:
                print(f"\n{category}:")
                for cmd in sorted(matching_cmds):
                    print(f"  - {cmd}")

        all_categorized = set()
        for prefixes in categories.values():
            for prefix in prefixes:
                all_categorized.update(
                    [cmd for cmd in available_cmds if cmd.startswith(prefix)]
                )

        remaining = set(available_cmds) - all_categorized
        if remaining:
            print("\nMiscellaneous:")
            for cmd in sorted(remaining):
                print(f"  - {cmd}")

        print("\nType 'help <command>' for details about a specific command.")
        return

    cmd = command.strip().lower()
    if cmd in COMMAND_HELP:
        print(f"\nHelp for '{cmd}':\n  {COMMAND_HELP[cmd]}")

        extended_help = get_extended_help(cmd)
        if extended_help:
            print(f"\n{extended_help}")

        return

    if adapter and hasattr(adapter, "get_help"):
        try:
            specific_help = adapter.get_help(command.upper())
            if specific_help:
                print(
                    f"\n[{adapter.__class__.__name__}] help for"
                    f" '{command.upper()}':\n  {specific_help}"
                )
                return
        except Exception as e:
            print(f"[Error fetching device-specific help]: {e}")

    print(f"No help found for '{command}'.")


# ------------------------------------------------------------------------------
# COMMAND PARSER
# ------------------------------------------------------------------------------
def parse_command(input_str, COMMANDS):
    """
    Parse user input into a command and its arguments.

    Parameters:
        input_str (str): User input string.
        COMMANDS (dict): Dictionary of available commands.

    Returns:
        tuple: Parsed command and arguments.
    """
    parts = input_str.strip().split()
    if not parts:
        return "", ""

    if parts[0].lower() == "get":
        parts[0] = "read"
    elif parts[0].lower() == "set":
        parts[0] = "write"

    for i in range(min(3, len(parts)), 0, -1):
        candidate = " ".join(parts[:i]).lower()
        if candidate in COMMANDS:
            return candidate, " ".join(parts[i:])
    return parts[0].lower(), " ".join(parts[1:])


# ------------------------------------------------------------------------------
# MAIN INTERACTIVE COMMAND LOOP
# ------------------------------------------------------------------------------
def main_loop(adapter, ser, COMMANDS, COMMAND_HELP, machine_mode=False):
    """
    REPL-style loop that prompts the user for commands and executes them.

    Parameters:
        adapter (object): Scanner adapter instance.
        ser (serial.Serial): Serial connection to the scanner.
        COMMANDS (dict): Dictionary of available commands.
        COMMAND_HELP (dict): Dictionary of help texts for commands.
        machine_mode (bool): Whether to use machine-friendly output.
    """
    print("Type 'help' for a list of commands.\n")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            break

        command, args = parse_command(user_input, COMMANDS)
        handler = COMMANDS.get(command)

        if handler:
            try:
                result = handler(args) if args else handler()

                if result is not None:
                    if isinstance(result, bytes):
                        formatted_result = result.decode(
                            "ascii", errors="replace"
                        ).strip()
                    elif isinstance(result, (int, float)):
                        formatted_result = str(result)
                    else:
                        formatted_result = str(result)

                    if machine_mode:
                        print(
                            "OK"
                            if not formatted_result.lower().startswith("error")
                            else "ERROR"
                        )
                    else:
                        print(formatted_result)

            except Exception as e:
                logging.error(f"Command error: {str(e)}", exc_info=True)
                print(f"[Error] {e}")
        else:
            print("Unknown command. Type 'help' for options.")


# ------------------------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------------------------
class TimeoutError(Exception):
    """Exception raised when an operation times out."""

    pass


def with_timeout(timeout_seconds, default_result=None):
    """
    Decorator to apply timeout to a function.

    Parameters:
        timeout_seconds (float): Maximum time in seconds to allow function to
        run.
        default_result: Value to return if timeout occurs, or raise
        TimeoutError if None.

    Returns:
        Decorated function with timeout capability.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [default_result]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)

            if thread.is_alive():
                if default_result is None:
                    raise TimeoutError(
                        f"Operation timed out after {timeout_seconds} seconds"
                    )
                return default_result

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper

    return decorator


def main():
    """
    Main program entry point.

    Detects scanner, sets up adapter, and launches command loop.
    """
    parser = argparse.ArgumentParser(description="Scanner Interface")
    parser.add_argument(
        "--machine",
        action="store_true",
        help="Use machine-friendly output (no icons)",
    )
    args = parser.parse_args()

    machine_mode = args.machine

    print("Searching for connected scanners...")
    detected = find_all_scanner_ports()

    if not detected:
        print("\nNo scanners found. Troubleshooting steps:")
        print("  1. Check that your scanner is powered on")
        print("  2. Verify USB connections are secure")
        print("  3. Try a different USB port or cable")
        print("  4. Restart your scanner")
        print(
            "  5. Check device manager to confirm the scanner is recognized"
            "by your computer"
        )

        if (
            input("\nWould you like to run connection diagnostics? (y/n): ")
            .lower()
            .startswith("y")
        ):
            diagnose_connection_issues()

        logging.error("No scanners found. Exiting.")
        return

    print("Scanners detected:")
    for scannerPortIndex, (port, model) in enumerate(detected, 1):
        print(f"  {scannerPortIndex}. {port} — {model}")

    try:
        if scannerPortIndex == 1:
            selection = 1
        else:
            selection = int(
                input(
                    "\nSelect a scanner to connect to (enter number or "
                    "0 to exit): "
                )
            )
        if selection == 0:
            print("Exiting.")
            return
        if 1 <= selection <= len(detected):
            port, scanner_model = detected[selection - 1]
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input. Exiting.")
        return

    try:
        with serial.Serial(port, 115200, timeout=1.0, write_timeout=1.0) as ser:

            @with_timeout(30)
            def initialize_adapter():
                return get_scanner_adapter(scanner_model, machine_mode)

            try:
                adapter = initialize_adapter()
                if not adapter:
                    print(f"No adapter implemented for {scanner_model}.")
                    return

                print(f"Connected to {port} ({scanner_model})")

                COMMANDS, COMMAND_HELP = build_command_table(adapter, ser)

                COMMANDS["help"] = lambda arg="": show_help(
                    COMMANDS, COMMAND_HELP, arg, adapter
                )

                initialize_readline(COMMANDS)

                main_loop(adapter, ser, COMMANDS, COMMAND_HELP, machine_mode)

            except TimeoutError:
                print(
                    "Timeout while initializing scanner adapter. Scanner"
                    " may be unresponsive."
                )
                logging.error("Timeout while initializing scanner adapter")
                return

    except Exception as e:
        logging.error(f"Error communicating with scanner: {e}")
        print(f"Error communicating with scanner: {e}")


# ------------------------------------------------------------------------------
# PROGRAM START
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
