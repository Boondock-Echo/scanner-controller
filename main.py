"""
Scanner Controller main module.

This is the main entry point for the scanner controller application.
It provides command-line interface for interacting with various scanner models
through their respective adapters.
"""

# Standard library imports
import argparse
import logging
import threading

import serial

# Application imports
from utilities.core.command_registry import build_command_table

# Local application/relative imports
# Replace legacy imports with utilities
from utilities.core.scanner_utils import find_all_scanner_ports
from utilities.core.shared_utils import diagnose_connection_issues
from utilities.help_topics import get_extended_help
from utilities.log_utils import configure_logging
from utilities.readlineSetup import initialize_readline
from utilities.scanner_factory import get_scanner_adapter

# ------------------------------------------------------------------------------
# LOGGING SETUP
# ------------------------------------------------------------------------------

# Configure logging
logger = configure_logging(level=logging.DEBUG)

# ------------------------------------------------------------------------------
# SUPPORTED SCANNER ADAPTERS
# ------------------------------------------------------------------------------

# Maps scanner model names to their respective adapter instances
# Using scanner_factory instead of direct imports
adapter_scanner = {
    "BC125AT": get_scanner_adapter("BC125AT"),
    "BCD325P2": get_scanner_adapter("BCD325P2"),
}

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
    # Display help for a specific command
    if command:
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
        return

    # Display general help (no specific command provided)
    print("\nAvailable Commands:")
    print("=================")

    # 1. General scanner commands (from adapter)
    # Update to use get/set as primary command categories
    general_commands = {
        "Get Commands": [
            cmd for cmd in sorted(COMMANDS) if cmd.startswith("get ")
        ],
        "Set Commands": [
            cmd for cmd in sorted(COMMANDS) if cmd.startswith("set ")
        ],
        "Controlling Scanner": [
            cmd
            for cmd in sorted(COMMANDS)
            if cmd.startswith(("hold ", "send ", "dump "))
        ],
        "Other": ["help", "exit"],
    }

    for category, cmds in general_commands.items():
        if cmds:
            print(f"\n{category}:")
            # Format in columns (3 columns)
            for i in range(0, len(cmds), 3):
                row = cmds[i : i + 3]
                print("  " + "  ".join(f"{cmd:<20}" for cmd in row))

    # 2. Device-specific commands from command libraries
    if adapter and hasattr(adapter, "commands"):
        print("\nDevice-Specific Commands:")
        print("=======================")

        # Get all commands from the adapter
        all_commands = adapter.commands

        # Dynamically discover command categories
        command_groups = {}
        for cmd_name, cmd_obj in all_commands.items():
            # Skip commands that are already covered in the general commands
            if any(
                cmd_name.lower() == gc.lower()
                for gc in sum(general_commands.values(), [])
            ):
                continue

            # Get the source module if available, or use "Other Commands"
            if hasattr(cmd_obj, 'source_module') and cmd_obj.source_module:
                # Format the category name more nicely
                category_name = cmd_obj.source_module.replace('_', ' ').title()
                # Remove "Commands" if it appears at the end to avoid redundancy
                if category_name.endswith(" Commands"):
                    category_name = category_name[:-9]
            else:
                category_name = "Other Commands"

            # Add command to its category
            if category_name not in command_groups:
                command_groups[category_name] = []
            command_groups[category_name].append(cmd_name)

        # Display commands by category
        for category_name in sorted(command_groups.keys()):
            commands = sorted(command_groups[category_name])
            if commands:
                print(f"\n{category_name}:")
                # Format in columns (5 columns for these shorter commands)
                for i in range(0, len(commands), 5):
                    row = commands[i : i + 5]
                    print("  " + "  ".join(f"{cmd:<8}" for cmd in row))

    print("\nType 'help <command>' for details about a specific command.")
    print("Example: 'help get frequency' or 'help CNT'")


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

    Supports aliases: 'read' → 'get' and 'write' → 'set'.
    Attempts to match the longest prefix first (up to 3 words).
    """
    parts = input_str.strip().split()
    if not parts:
        return "", ""

    # Convert legacy read/write commands to get/set
    if parts[0].lower() == "read":
        parts[0] = "get"
    elif parts[0].lower() == "write":
        parts[0] = "set"

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
    Run the main interactive command loop.

    Provides a REPL-style interface that prompts for commands and executes
    them using the COMMANDS dictionary.

    Args:
        adapter (object): The scanner adapter instance.
        ser (serial.Serial): The serial connection to the scanner.
        COMMANDS (dict): Dictionary mapping command names to handler functions.
        COMMAND_HELP (dict): Dictionary mapping command names to help strings.
        machine_mode (bool, optional): Whether to use machine-friendly output.
            Defaults to False.
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
                logger.error(f"Command error: {str(e)}", exc_info=True)
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
    Apply timeout to a function.

    Parameters:
        timeout_seconds (float): Maximum time in seconds to allow function to
        run.
        default_result: Value to return if timeout occurs, or raise
        TimeoutError if None.

    Returns:
        Function with timeout capability.
    """

    def timeout_function(func):
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

    return timeout_function


def main():
    """
    Enter main program.

    Detects scanner, sets up adapter, and launches command loop.

    Execute the main program.

    This is the main entry point for the application. It detects connected
    scanners, sets up the appropriate adapter, and launches the command loop.
    """
    # ----------------------------------------
    # Parse CLI options
    # ----------------------------------------
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

        logger.error("No scanners found. Exiting.")
        return

    print("Scanners detected:")
    for scannerPortIndex, (port, model) in enumerate(detected, 1):
        print(f"  {scannerPortIndex}. {port} — {model}")

    try:
        if len(detected) == 1:
            selection = 1  # Auto-select if only one scanner is found
        else:
            try:
                selection = int(
                    input(
                        "\nSelect a scanner to connect to"
                        "(enter number or 0 to exit): "
                    )
                )
                if selection == 0:  # Exit if user selects 0
                    print("Exiting.")
                    return
            except ValueError:
                print("Invalid input. Exiting.")
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

                # Inject help command after table is built
                # for access to help dictionary
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
                logger.error("Timeout while initializing scanner adapter")
                return

    except Exception as e:
        logger.error(f"Error communicating with scanner: {e}")
        print(f"Error communicating with scanner: {e}")


# ------------------------------------------------------------------------------
# PROGRAM START
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
