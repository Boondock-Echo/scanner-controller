import os
import logging
import serial
import argparse
from utilities.log_trim import trim_log_file
from scanner_adapters.scanner_utils import find_all_scanner_ports
from scanner_adapters.bc125atAdapter import BC125ATAdapter
from scanner_adapters.bcd325p2Adapter import BCD325P2Adapter
from scanner_adapters.sds100Adapter import SDS100Adapter
from scanner_adapters.aordv1Adapter import AORDV1Adapter
from command_registry import build_command_table
from utilities.readlineSetup import initialize_readline

# ------------------------------------------------------------------------------
# LOGGING SETUP
# ------------------------------------------------------------------------------

# Configure log file for debugging and error tracking
# (Note: logging is not used in this script, but may be useful for debugging)
logging.basicConfig(
    filename="scanner_tool.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

if not os.path.exists("scanner_tool.log"):
    logging.error("Log file not found. Creating a new one.")    

if os.path.getsize("scanner_tool.log") > 10 * 1024 * 1024:  # 10 MB limit
    logging.info("Log file size exceeded 10 MB. Trimming...")
    trim_log_file("scanner_tool.log", max_size=10 * 1024 * 1024)  # Keep the log file manageable

# ------------------------------------------------------------------------------
# SUPPORTED SCANNER ADAPTERS
# ------------------------------------------------------------------------------

# Maps scanner model names to their respective adapter classes
SCANNER_ADAPTERS = { # if your scanner adapter is not listed here, add it here
    "BC125AT": BC125ATAdapter(),
    "BCD325P2": BCD325P2Adapter(),  # Ensure this is correctly instantiated
    "SDS100": SDS100Adapter(),
    "AOR-DV1": AORDV1Adapter(),
}

# ------------------------------------------------------------------------------
# HELP COMMAND
# ------------------------------------------------------------------------------
# This function is used to display help for a given command.
# If no command is given, it lists available commands.
# If the command matches a high-level command (e.g., 'read volume'), it uses COMMAND_HELP.
# If connected to a scanner and help is not found above, it attempts to fetch help from the device-specific command library.
# If no help is found, it prints "No help found for '{command}'."
# If an error occurs while fetching device-specific help, it prints "[Error fetching device-specific help]: {e}".
# This function is used in the main_loop function.
def show_help(COMMANDS, COMMAND_HELP, command="", adapter=None):
    # Display general help if no command is provided
    # Display help for a specific command if provided
    if not command:
        print("\nAvailable commands:")
        for cmd in sorted(COMMANDS):
            print(f"  - {cmd}")
        print("\nType 'help <command>' for details.")
        return
    # Display help for a specific command
    # If the command is in COMMAND_HELP, print the help message
    # If the command is not in COMMAND_HELP, attempt to fetch device-specific help via adapter.getHelp("CMD")
    # If no help is found, print "No help found for '{command}'."
    # If an error occurs while fetching device-specific help, print "[Error fetching device-specific help]: {e}".
    
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
# This function is used to parse user input into a command and its arguments.
# It supports aliases like 'get' → 'read' and 'set' → 'write'.  
# This function is used in the main_loop function.
# The parse_command function takes two arguments: input_str and COMMANDS.

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
    detected = find_all_scanner_ports()

    if not detected:
        print("No scanners found. Exiting.")
        logging.error("No scanners found. Exiting.")
        return

    print("Scanners detected:")
    for scannerPortIndex, (port, model) in enumerate(detected, 1):
        print(f"  {scannerPortIndex}. {port} — {model}")

    # Prompt user to select a scanner from the detected list
    try:
        if scannerPortIndex == 1:
            selection = 1  # only one scanner found, auto-select
        else:  # multiple scanners found, prompt user to select        
            selection = int(input("\nSelect a scanner to connect to (enter number or 0 to exit): "))
        if selection == 0: # 0 to exit
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
    # Use the scanner model to select the appropriate adapter
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