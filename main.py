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

    print(
        """
    ██   ██ ███████ ██      ██████      ███    ███ ███████ ███    ██ ██    ██
    ██   ██ ██      ██      ██   ██     ████  ████ ██      ████   ██ ██    ██
    ███████ █████   ██      ██████      ██ ████ ██ █████   ██ ██  ██ ██    ██
    ██   ██ ██      ██      ██          ██  ██  ██ ██      ██  ██ ██ ██    ██
    ██   ██ ███████ ███████ ██          ██      ██ ███████ ██   ████  ██████
          """
    )

    # 1. General scanner commands (from adapter)
    # Define standard high-level commands that should be available
    standard_commands = {
        "Get Commands": [
            "get frequency",
            "get volume",
            "get squelch",
            "get mode",
            "get status",
            "get channel",
            "get system",
            "get backlight",
            "get battery",
        ],
        "Set Commands": [
            "set frequency",
            "set volume",
            "set squelch",
            "set mode",
            "set backlight",
            "set contrast",
        ],
        "Controlling Scanner": [
            "hold frequency",
            "send key",
            "dump memory",
            "scan start",
            "scan stop",
        ],
        "Other": ["help", "exit"],
    }

    # Check if any high-level commands exist in COMMANDS
    has_high_level_commands = any(
        cmd.startswith(("get ", "set ", "hold ", "send ", "dump "))
        for cmd in COMMANDS
    )

    # Use compact display format for both high-level and device-specific
    # commands
    if has_high_level_commands:
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
    else:
        general_commands = standard_commands

    # 2. Get device-specific command categories for alignment calculation
    device_specific_categories = []
    if adapter and hasattr(adapter, "commands"):
        all_commands = adapter.commands
        command_groups = {}

        for cmd_name, cmd_obj in all_commands.items():
            # Skip commands already covered in general commands
            if any(
                cmd_name.lower() == gc.lower()
                for gc in sum(general_commands.values(), [])
            ):
                continue

            # Get category name
            if hasattr(cmd_obj, 'source_module') and cmd_obj.source_module:
                category_name = cmd_obj.source_module.replace('_', ' ').title()
                if category_name.endswith(" Commands"):
                    category_name = category_name[:-9]
            else:
                category_name = "Other"

            device_specific_categories.append(category_name)

            if category_name not in command_groups:
                command_groups[category_name] = []
            command_groups[category_name].append(cmd_name)

    # Find longest category name across both high-level and device-specific
    # commands
    all_categories = list(general_commands.keys()) + device_specific_categories
    max_category_length = (
        max(len(name) for name in all_categories) if all_categories else 0
    )

    # Display high-level commands using the grid format with aligned colons
    print(
        """
================================================================================
||                              Universal Commands                            ||
================================================================================
          """
    )
    cols_hl = 3  # Fewer columns for longer command names

    for category, cmds in general_commands.items():
        if cmds:
            # Print category name with aligned colon - using the global max
            # length
            print(f"{category:{max_category_length}}: ", end="")

            # Calculate indentation for wrapped lines
            indent = max_category_length + 2  # category length + colon + space

            # Print commands in a grid with appropriate spacing
            for i, cmd in enumerate(sorted(cmds)):
                # High-level commands are longer, so give them more space
                print(f"{cmd:<15}", end="  ")

                # Add newline and indentation for wrapped lines
                if (i + 1) % cols_hl == 0 and i < len(cmds) - 1:
                    print("\n" + " " * indent, end="")
            print()  # End line for category

    # 2. Device-specific commands from command libraries
    if adapter and hasattr(adapter, "commands"):
        print(
            """
================================================================================
||                          Device Specific Commands                          ||
================================================================================
              """
        )
        # Get all commands from the adapter
        all_commands = adapter.commands

        # Dynamically discover command categories
        command_groups = {}
        for cmd_name, cmd_obj in all_commands.items():
            # Skip commands already covered in general commands
            if any(
                cmd_name.lower() == gc.lower()
                for gc in sum(general_commands.values(), [])
            ):
                continue

            # Get category name
            if hasattr(cmd_obj, 'source_module') and cmd_obj.source_module:
                category_name = cmd_obj.source_module.replace('_', ' ').title()
                if category_name.endswith(" Commands"):
                    category_name = category_name[:-9]
            else:
                category_name = "Other"

            if category_name not in command_groups:
                command_groups[category_name] = []
            command_groups[category_name].append(cmd_name)

        # Find the longest category name for proper alignment
        if command_groups:
            max_category_length = max(
                len(name) for name in command_groups.keys()
            )
        else:
            max_category_length = 0

        # Display each category with aligned colons and consistent command
        # spacing
        cols = 5  # Number of columns in the grid

        for category_name in sorted(command_groups.keys()):
            commands = sorted(command_groups[category_name])
            if commands:
                # Print the category name with aligned colons
                print(f"{category_name:{max_category_length}}: ", end="")

                # Calculate indentation for wrapped lines
                indent = (
                    max_category_length + 2
                )  # category length + colon + space

                # Print commands with consistent spacing
                for i, cmd in enumerate(commands):
                    print(
                        f"{cmd:4}", end="  "
                    )  # 4 chars for command + 2 spaces

                    # Add newline and indentation for wrapped lines
                    if (i + 1) % cols == 0 and i < len(commands) - 1:
                        print("\n" + " " * indent, end="")
                print()  # End line for category

    print("\nType 'help <command>' for details about a specific command.")


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
class ScannerTimeoutError(Exception):
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
                    raise ScannerTimeoutError(
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

            except ScannerTimeoutError:
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
