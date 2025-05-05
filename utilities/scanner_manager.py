"""
Scanner management utilities.

This module contains functions for managing scanner connections and switching.
"""

import logging

import serial

from utilities.core.command_registry import build_command_table
from utilities.core.scanner_utils import find_all_scanner_ports
from utilities.scanner_factory import get_scanner_adapter
from utilities.timeout_utils import with_timeout

logger = logging.getLogger(__name__)


def switch_scanner(
    current_ser, current_adapter, machine_mode=False, direct_scanner_id=None
):
    """
    Switch to a different scanner without exiting the application.

    Parameters:
        current_ser (serial.Serial): Current serial connection to close.
        current_adapter: Current adapter instance.
        machine_mode (bool): Whether to use machine-friendly output.
        direct_scanner_id (int, optional): Direct scanner ID to connect to,
            bypassing scan selection.

    Returns:
        tuple: (new_ser, new_adapter, new_commands, new_command_help) or None if
        canceled/error
    """
    # Clean up current connection
    try:
        if current_ser and current_ser.is_open:
            logger.info("Closing current scanner connection")
            current_ser.close()
    except Exception as e:
        logger.error(f"Error closing current connection: {e}")

    if machine_mode:
        print("STATUS:INFO|ACTION:DETECTING_SCANNERS")
    else:
        print("\nDetecting available scanners...")

    detected = find_all_scanner_ports()

    if not detected:
        if machine_mode:
            print("STATUS:ERROR|CODE:NO_SCANNERS_FOUND")
        else:
            print("No scanners found. Check connections and try again.")
        # Reopen the previous connection if possible
        try:
            if not current_ser.is_open:
                current_ser.open()
            return None
        except Exception as e:
            logger.error(f"Error reopening previous connection: {e}")
            return None

    # Display available scanners
    if machine_mode:
        print(f"STATUS:INFO|SCANNERS_FOUND:{len(detected)}")
        for idx, (port, model) in enumerate(detected, 1):
            print(f"SCANNER:{idx}|PORT:{port}|MODEL:{model}")
    else:
        print("\nAvailable scanners:")
        for idx, (port, model) in enumerate(detected, 1):
            print(f"  {idx}. {port} — {model}")

    # Get user selection or use direct scanner ID
    try:
        if direct_scanner_id is not None:
            # Use the directly provided scanner ID
            selection = int(direct_scanner_id)
            if not (1 <= selection <= len(detected)):
                if machine_mode:
                    print(
                        "STATUS:ERROR|CODE:INVALID_SCANNER_ID|MAX_ID:"
                        f"{len(detected)}"
                    )
                else:
                    print(
                        f"Invalid scanner ID: {selection}. Must be between 1 "
                        f"and {len(detected)}."
                    )
                # Reopen previous connection
                try:
                    if not current_ser.is_open:
                        current_ser.open()
                    return None
                except Exception as e:
                    logger.error(f"Error reopening previous connection: {e}")
                    return None
        elif machine_mode:
            # In machine mode without direct ID, auto-select the first scanner
            selection = 1
            print(f"STATUS:INFO|AUTO_SELECTED:{selection}")
        else:
            # Interactive selection for normal mode
            try:
                selection = input(
                    "\nSelect scanner (enter number or 0 to cancel): "
                )
                if selection.strip() == "0" or not selection.strip():
                    print("Switch canceled, reconnecting to current scanner...")
                    # Reopen the previous connection
                    try:
                        if not current_ser.is_open:
                            current_ser.open()
                        return None
                    except Exception as e:
                        logger.error(
                            f"Error reopening previous connection: {e}"
                        )
                        return None

                selection = int(selection)
                if not (1 <= selection <= len(detected)):
                    print(
                        "Invalid selection, reconnecting to current scanner..."
                    )
                    # Reopen the previous connection
                    try:
                        if not current_ser.is_open:
                            current_ser.open()
                        return None
                    except Exception as e:
                        logger.error(
                            f"Error reopening previous connection: {e}"
                        )
                        return None
            except ValueError:
                print("Invalid input, reconnecting to current scanner...")
                # Reopen the previous connection
                try:
                    if not current_ser.is_open:
                        current_ser.open()
                    return None
                except Exception as e:
                    logger.error(f"Error reopening previous connection: {e}")
                    return None
    except Exception as e:
        if machine_mode:
            error_msg = str(e).replace(" ", "_").replace(":", "_")
            print(f"STATUS:ERROR|CODE:SELECTION_ERROR|MESSAGE:{error_msg}")
        else:
            print(f"Error selecting scanner: {e}")
        # Try to reopen the previous connection
        try:
            if not current_ser.is_open:
                current_ser.open()
            return None
        except Exception as reconnect_error:
            logger.error(
                f"Error reopening previous connection: {reconnect_error}"
            )
            return None

    # Connect to selected scanner
    port, scanner_model = detected[selection - 1]

    try:
        # Create new connection
        new_ser = serial.Serial(port, 115200, timeout=1.0, write_timeout=1.0)

        # Initialize adapter
        @with_timeout(30)
        def initialize_adapter():
            return get_scanner_adapter(scanner_model, machine_mode)

        new_adapter = initialize_adapter()
        if not new_adapter:
            if machine_mode:
                print(f"STATUS:ERROR|CODE:NO_ADAPTER|MODEL:{scanner_model}")
            else:
                print(
                    f"No adapter implemented for {scanner_model}, "
                    "reconnecting to previous scanner..."
                )
            new_ser.close()
            # Reopen previous connection
            try:
                if not current_ser.is_open:
                    current_ser.open()
                return None
            except Exception as e:
                logger.error(f"Error reopening previous connection: {e}")
                return None

        # Build new command table
        new_commands, new_command_help = build_command_table(
            new_adapter, new_ser
        )

        if machine_mode:
            print(
                f"STATUS:OK|ACTION:SWITCHED|PORT:{port}|MODEL:{scanner_model}"
            )
        else:
            print(f"\nSuccessfully switched to {port} ({scanner_model})")
        return (new_ser, new_adapter, new_commands, new_command_help)

    except Exception as e:
        logger.error(f"Error connecting to new scanner: {e}")
        if machine_mode:
            error_msg = str(e).replace(" ", "_").replace(":", "_")
            print(f"STATUS:ERROR|CODE:CONNECTION_FAILED|MESSAGE:{error_msg}")
        else:
            print(f"Error connecting to new scanner: {e}")
        # Try to reopen the previous connection
        try:
            if not current_ser.is_open:
                current_ser.open()
            return None
        except Exception as reconnect_error:
            logger.error(
                f"Error reopening previous connection: {reconnect_error}"
            )
            return None


def handle_switch_command(
    ser, adapter, commands, command_help, machine_mode, scanner_id=None
):
    """
    Switch command handler for the scanner.

    Handler for the switch command that switches scanners.

    Parameters:
        ser (serial.Serial): Current serial connection.
        adapter: Current adapter instance.
        commands (dict): Dictionary of available commands.
        command_help (dict): Dictionary of help texts for commands.
        machine_mode (bool): Whether to use machine-friendly output.
        scanner_id (str, optional): Scanner ID to directly connect to.
    """
    direct_id = None
    if scanner_id:
        try:
            direct_id = int(scanner_id)
        except ValueError:
            if machine_mode:
                return (
                    "STATUS:ERROR|CODE:INVALID_SCANNER_ID|"
                    "MESSAGE:Scanner_ID_must_be_a_number"
                )
            else:
                return f"Invalid scanner ID: {scanner_id}. Must be a number."

    result = switch_scanner(ser, adapter, machine_mode, direct_id)
    if result:
        # Return the new connection info to be handled in main_loop
        return result
    return "Scanner switch canceled or failed"


def detect_and_connect_scanner(machine_mode=False):
    """
    Detect available scanners and connect to one selected by the user.

    Parameters:
        machine_mode (bool): Whether to use machine-friendly output.

    Returns:
        tuple: (ser, adapter, commands, command_help) or
        (None, None, None, None) if failed
    """
    if machine_mode:
        print("STATUS:INFO|ACTION:SCANNING_FOR_DEVICES")
    else:
        print("Searching for connected scanners...")

    detected = find_all_scanner_ports()

    if not detected:
        if machine_mode:
            print("STATUS:ERROR|CODE:NO_SCANNERS_FOUND")
        else:
            print("\nNo scanners found. Troubleshooting steps:")
            print("  1. Check that your scanner is powered on")
            print("  2. Verify USB connections are secure")
            print("  3. Try a different USB port or cable")
            print("  4. Restart your scanner")
            print(
                "  5. Check device manager to confirm the scanner is recognized"
                "by your computer"
            )
        return None, None, None, None

    if machine_mode:
        print(f"STATUS:INFO|SCANNERS_FOUND:{len(detected)}")
        for idx, (port, model) in enumerate(detected, 1):
            print(f"SCANNER:{idx}|PORT:{port}|MODEL:{model}")
    else:
        print("Scanners detected:")
        for scannerPortIndex, (port, model) in enumerate(detected, 1):
            print(f"  {scannerPortIndex}. {port} — {model}")

    try:
        if len(detected) == 1 or machine_mode:
            selection = 1  # Auto-select if only one scanner or in machine mode
            if machine_mode:
                print(f"STATUS:INFO|AUTO_SELECTED:{selection}")
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
                    return None, None, None, None
            except ValueError:
                print("Invalid input. Exiting.")
                return None, None, None, None

        if 1 <= selection <= len(detected):
            port, scanner_model = detected[selection - 1]
        else:
            if machine_mode:
                print("STATUS:ERROR|CODE:INVALID_SELECTION")
            else:
                print("Invalid selection.")
            return None, None, None, None
    except ValueError:
        print("Invalid input. Exiting.")
        return None, None, None, None

    try:
        ser = serial.Serial(port, 115200, timeout=1.0, write_timeout=1.0)

        @with_timeout(30)
        def initialize_adapter():
            return get_scanner_adapter(scanner_model, machine_mode)

        adapter = initialize_adapter()
        if not adapter:
            if machine_mode:
                print(f"STATUS:ERROR|CODE:NO_ADAPTER|MODEL:{scanner_model}")
            else:
                print(f"No adapter implemented for {scanner_model}.")
            ser.close()
            return None, None, None, None

        if machine_mode:
            print(
                f"STATUS:OK|ACTION:CONNECTED|PORT:{port}|MODEL:{scanner_model}"
            )
        else:
            print(f"Connected to {port} ({scanner_model})")

        commands, command_help = build_command_table(adapter, ser)
        return ser, adapter, commands, command_help

    except Exception as e:
        logger.error(f"Error communicating with scanner: {e}")
        if machine_mode:
            error_msg = str(e).replace(" ", "_").replace(":", "_")
            print(f"STATUS:ERROR|CODE:COMMUNICATION_FAILED|MESSAGE:{error_msg}")
        else:
            print(f"Error communicating with scanner: {e}")
        return None, None, None, None


def scan_for_scanners():
    """
    Scan for available scanners and return the list.

    This command is primarily for machine mode to list scanners
    without automatically connecting.

    Returns:
        str: Machine-readable list of available scanners
    """
    logger.info("Scanning for connected scanners")

    detected = find_all_scanner_ports()

    if not detected:
        return "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"

    result = f"STATUS:OK|SCANNERS_FOUND:{len(detected)}"
    for idx, (port, model) in enumerate(detected, 1):
        result += f"|SCANNER:{idx}|PORT:{port}|MODEL:{model}"

    return result


def connect_to_scanner(
    scanner_id, existing_commands=None, existing_command_help=None
):
    """
    Connect to a specific scanner by its ID (from scan_for_scanners).

    Parameters:
        scanner_id (str): Scanner ID from the scan results
        existing_commands (dict): Existing commands dictionary to update
        existing_command_help (dict): Existing command help dictionary to update

    Returns:
        tuple: (ser, adapter, commands, command_help) if successful,
               or an error message string if failed
    """
    try:
        scanner_id = int(scanner_id)
    except ValueError:
        return (
            "STATUS:ERROR|CODE:INVALID_SCANNER_ID|"
            "MESSAGE:Scanner_ID_must_be_a_number"
        )

    # Get the list of available scanners
    detected = find_all_scanner_ports()

    if not detected:
        return "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"

    if not (1 <= scanner_id <= len(detected)):
        return f"STATUS:ERROR|CODE:INVALID_SCANNER_ID|MAX_ID:{len(detected)}"

    # Get the selected scanner
    port, scanner_model = detected[scanner_id - 1]

    try:
        # Connect to the scanner
        ser = serial.Serial(port, 115200, timeout=1.0, write_timeout=1.0)

        @with_timeout(30)
        def initialize_adapter():
            return get_scanner_adapter(
                scanner_model, True
            )  # Always use machine mode formatting

        adapter = initialize_adapter()
        if not adapter:
            if ser.is_open:
                ser.close()
            return f"STATUS:ERROR|CODE:NO_ADAPTER|MODEL:{scanner_model}"

        # Build command table
        commands, command_help = build_command_table(adapter, ser)

        # If we need to merge with existing commands
        if existing_commands is not None and existing_command_help is not None:
            # We'll return these commands to be merged by the caller
            pass

        return (ser, adapter, commands, command_help)

    except Exception as e:
        logger.error(f"Error communicating with scanner: {e}")
        error_msg = str(e).replace(" ", "_").replace(":", "_")
        return f"STATUS:ERROR|CODE:COMMUNICATION_FAILED|MESSAGE:{error_msg}"
