"""
Scanner Controller main module.

This is the main entry point for the scanner controller application.
It provides command-line interface for interacting with various scanner models
through their respective adapters.
"""

# Standard library imports
import argparse
import importlib
import logging
import threading

import serial

# Local application/relative imports
from adapter_scanner.adapter_bc125at import BC125ATAdapter
from adapter_scanner.adapter_bcd325p2 import BCD325P2Adapter
from adapter_scanner.scanner_utils import find_all_scanner_ports

# Application imports
from utilities.core.command_registry import build_command_table
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

# Maps scanner model names to their respective adapter classes
adapter_scanner = {
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


adapter_scanner = {  # if your scanner adapter is not listed here, add it here
    "BC125AT": BC125ATAdapter(),
    "BCD325P2": BCD325P2Adapter(),
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
    Display help information for commands.

    This function displays help for a given command. If no command is given,
    it lists available commands. It attempts to fetch help from the
    device-specific command library if connected to a scanner and help is not
    found elsewhere.

    Args:
        COMMANDS (dict): Dictionary mapping command names to handler functions.
        COMMAND_HELP (dict): Dictionary mapping command names to help strings.
        command (str, optional): The command to show help for. Defaults to "".
        adapter (object, optional): The scanner adapter. Defaults to None.
    """
    # Display general help if no command is provided
    # Display help for a specific command if provided
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
        for cmd in sorted(COMMANDS):
            print(f"--->{cmd}")
        print("\nType 'help <command>' for details.")
        return

    # Display help for a specific command
    # If the command is in COMMAND_HELP, print the help message
    # If the command is not in COMMAND_HELP, attempt to fetch device-specific
    # help via adapter.getHelp("CMD")
    # If no help is found, print "No help found for '{command}'."
    # If an error occurs while fetching device-specific help, print
    # "[Error fetching device-specific help]: {e}".

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
                print(
                    f"\n[{adapter.__class__.__name__}] help for "
                    f"'{command.upper()}':\n  {specific_help}"
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
    Parse user input into a command and its arguments.

    Supports aliases like 'get' → 'read' and 'set' → 'write'.
    Attempts to match the longest prefix first (up to 3 words).

    Args:
        input_str (str): The raw user input string.
        COMMANDS (dict): Dictionary of available commands.

    Returns:
        tuple: A tuple of (command, arguments).
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
                        print(
                            "OK"
                            if not str(result).lower().startswith("error")
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
            selection = 1  # only one scanner found, auto-select
        else:  # multiple scanners found, prompt user to select
            selection = int(
                input(
                    "\nSelect a scanner to connect to "
                    "(enter number or 0 to exit): "
                )
            )
        if selection == 0:  # 0 to exit
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
