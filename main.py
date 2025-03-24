import logging
import serial
import time
from scannerUtils import clear_serial_buffer, read_response, send_command, findAllScannerPorts
from scannerAdapters.bc125atAdapter import BC125ATAdapter
from scannerAdapters.bcd325p2Adapter import BCD325P2Adapter
from scannerAdapters.sds100Adapter import SDS100Adapter
from scannerAdapters.aordv1Adapter import AORDV1Adapter
from commandRegistry import build_command_table
from readlineSetup import initialize_readline
import argparse

# ------------------------------------------------------------------------------
# LOGGING SETUP
# ------------------------------------------------------------------------------

# Configure log file for debugging and error tracking
logging.basicConfig(
    filename="scanner_tool.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ------------------------------------------------------------------------------
# SUPPORTED SCANNER ADAPTERS
# ------------------------------------------------------------------------------

# Maps scanner model names to their respective adapter classes
SCANNER_ADAPTERS = {
    "BC125AT": BC125ATAdapter(),
    "BCD325P2": BCD325P2Adapter(),
    "SDS100": SDS100Adapter(),
    "AOR-DV1": AORDV1Adapter(),
}

# ------------------------------------------------------------------------------
# HELP COMMAND
# ------------------------------------------------------------------------------

def show_help(COMMANDS, COMMAND_HELP, command="", adapter=None):
    """
    Displays help for a given command.

    - If no command is given: lists available commands
    - If command matches a high-level command (e.g. 'read volume'), uses COMMAND_HELP
    - If connected to a scanner and help is not found above, attempts to fetch help from the device-specific command library
    """
    if not command:
        print("\nAvailable commands:")
        for cmd in sorted(COMMANDS):
            print(f"  - {cmd}")
        print("\nType 'help <command>' for details.")
        return

    cmd = command.strip().lower()
    if cmd in COMMAND_HELP:
        print(f"\nHelp for '{cmd}':\n  {COMMAND_HELP[cmd]}")
        return

    # Attempt scanner-specific help via adapter.getHelp("CMD")
    if adapter and hasattr(adapter, "getHelp"):
        try:
            specific_help = adapter.getHelp(command.upper())
            if specific_help:
                print(f"\n[{adapter.__class__.__name__}] help for '{command.upper()}':\n  {specific_help}")
                return
        except Exception as e:
            print(f"[Error fetching device-specific help]: {e}")

    print(f"No help found for '{command}'.")

# ------------------------------------------------------------------------------
# COMMAND PARSER
# ------------------------------------------------------------------------------

def parse_command(input_str, COMMANDS):
    """
    Parses user input into a command and its arguments.
    Supports aliases like 'get' → 'read' and 'set' → 'write'.
    """
    parts = input_str.strip().split()
    if not parts:
        return "", ""

    # Normalize aliases
    if parts[0].lower() == "get":
        parts[0] = "read"
    elif parts[0].lower() == "set":
        parts[0] = "write"

    # Try to match longest prefix first (up to 3 words)
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
    REPL-style loop that prompts the user for commands and executes them using the COMMANDS dictionary.
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
                    if machine_mode:
                        print("OK" if not str(result).lower().startswith("error") else "ERROR")
                    else:
                        print(result)

            except Exception as e:
                print(f"[Error] {e}")
        else:
            print("Unknown command. Type 'help' for options.")

# ------------------------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------------------------

def main():
# ----------------------------------------
# Parse CLI options
# ----------------------------------------
    parser = argparse.ArgumentParser(description="Scanner Interface")
    parser.add_argument("--machine", action="store_true", help="Use machine-friendly output (no icons)")
    args = parser.parse_args()

    machine_mode = args.machine
    
    """
    Main program entry point. Detects scanner, sets up adapter, and launches command loop.
    """
    
    print("Searching for connected scanners...")
    detected = findAllScannerPorts()

    if not detected:
        print("No scanners found. Exiting.")
        logging.error("No scanners found. Exiting.")
        return

    print("Scanners detected:")
    for idx, (port, model) in enumerate(detected, 1):
        print(f"  {idx}. {port} — {model}")

    # Prompt user to select a scanner from the detected list
    try:
        selection = int(input("\nSelect a scanner to connect to (enter number or 0 to exit): "))
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

    # Open serial connection to the selected scanner
    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            adapter = SCANNER_ADAPTERS.get(scanner_model)
            if not adapter:
                print(f"No adapter implemented for {scanner_model}.")
                return

            print(f"Connected to {port} ({scanner_model})")

            # Build command dispatcher and help map dynamically
            COMMANDS, COMMAND_HELP = build_command_table(adapter, ser)

            # Inject help command after table is built (for access to help dict)
            COMMANDS["help"] = lambda arg="": show_help(COMMANDS, COMMAND_HELP, arg, adapter)

            initialize_readline(COMMANDS)

            # Enter interactive command loop
            main_loop(adapter, ser, COMMANDS, COMMAND_HELP, machine_mode)

    except Exception as e:
        logging.error(f"Error communicating with scanner: {e}")
        print(f"Error communicating with scanner: {e}")

# ------------------------------------------------------------------------------
# PROGRAM START
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
