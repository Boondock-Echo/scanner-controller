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


def switch_scanner(current_ser, current_adapter, machine_mode=False):
    """
    Switch to a different scanner without exiting the application.

    Parameters:
        current_ser (serial.Serial): Current serial connection to close.
        current_adapter: Current adapter instance.
        machine_mode (bool): Whether to use machine-friendly output.

    Returns:
        tuple: (new_ser, new_adapter, new_commands, new_command_help) or None if
        canceled/error
    """
    # Clean up current connection
    try:
        if (
            current_ser
            and hasattr(current_ser, 'is_open')
            and current_ser.is_open
        ):
            logger.info("Closing current scanner connection")
            current_ser.close()
    except Exception as e:
        logger.error(f"Error closing current connection: {e}")

    if machine_mode:
        print("STATUS:INFO|ACTION:DETECTING_SCANNERS")
    else:
        print("\nDetecting available scanners...")

    # Get current port and model if available
    current_port = None
    current_model = None
    if current_ser and hasattr(current_ser, 'port'):
        current_port = current_ser.port
        if current_adapter and hasattr(current_adapter, 'model'):
            current_model = current_adapter.model

    detected = find_all_scanner_ports(
        current_port=current_port, current_model=current_model
    )

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
        # In machine mode, don't auto-select - wait for explicit selection
        return None
    else:
        print("\nAvailable scanners:")
        for idx, (port, model) in enumerate(detected, 1):
            print(f"  {idx}. {port} — {model}")

    # Get user selection
    try:
        selection = input("\nSelect scanner (enter number or 0 to cancel): ")
        if selection.strip() == "0" or not selection.strip():
            print("Switch canceled, reconnecting to current scanner...")
            # Reopen the previous connection
            try:
                if not current_ser.is_open:
                    current_ser.open()
                return None
            except Exception as e:
                logger.error(f"Error reopening previous connection: {e}")
                return None

        selection = int(selection)
        if not (1 <= selection <= len(detected)):
            print("Invalid selection, reconnecting to current scanner...")
            # Reopen the previous connection
            try:
                if not current_ser.is_open:
                    current_ser.open()
                return None
            except Exception as e:
                logger.error(f"Error reopening previous connection: {e}")
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

        # Store the model in the adapter for reference
        new_adapter.model = scanner_model

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


def list_scanners(machine_mode=False, current_ser=None, current_adapter=None):
    """
    List all connected scanners without switching.

    Parameters:
        machine_mode (bool): Whether to use machine-friendly output.
        current_ser (serial.Serial): Current serial connection.
        current_adapter: Current adapter instance.

    Returns:
        str: Status message about the found scanners.
    """
    if machine_mode:
        print("STATUS:INFO|ACTION:LISTING_SCANNERS")
    else:
        print("\nScanning for connected devices...")

    # Get current port and model if available
    current_port = None
    current_model = None
    if current_ser and hasattr(current_ser, 'port'):
        current_port = current_ser.port
        if current_adapter and hasattr(current_adapter, 'model'):
            current_model = current_adapter.model

    detected = find_all_scanner_ports(
        current_port=current_port, current_model=current_model
    )

    if not detected:
        if machine_mode:
            return "STATUS:INFO|SCANNERS_FOUND:0"
        else:
            return "No scanners found. Check connections and try again."

    if machine_mode:
        result = f"STATUS:INFO|SCANNERS_FOUND:{len(detected)}"
        for idx, (port, model) in enumerate(detected, 1):
            result += f"\nSCANNER:{idx}|PORT:{port}|MODEL:{model}"
        return result
    else:
        result = f"Found {len(detected)} scanner(s):"
        for idx, (port, model) in enumerate(detected, 1):
            result += f"\n  {idx}. {port} — {model}"
        return result


def select_scanner(
    index, current_ser=None, current_adapter=None, machine_mode=False
):
    """
    Select and connect to a scanner by its index number.

    Parameters:
        index (str): Index number of the scanner to select (1-based).
        current_ser (serial.Serial): Current serial connection to close.
        current_adapter: Current adapter instance.
        machine_mode (bool): Whether to use machine-friendly output.

    Returns:
        tuple or str: (new_ser, new_adapter, new_commands, new_command_help) if
        successful, or error message if failed.
    """
    try:
        selection = int(index)
    except ValueError:
        if machine_mode:
            return (
                "STATUS:ERROR|CODE:INVALID_SELECTION|"
                "MESSAGE:Index_must_be_a_number"
            )
        else:
            return "Error: Selection must be a number."

    # Get current port and model if available
    current_port = None
    current_model = None
    if current_ser and hasattr(current_ser, 'port'):
        current_port = current_ser.port
        if current_adapter and hasattr(current_adapter, 'model'):
            current_model = current_adapter.model

    # Get the list of available scanners
    detected = find_all_scanner_ports(
        current_port=current_port, current_model=current_model
    )

    if not detected:
        if machine_mode:
            return "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"
        else:
            return "No scanners found. Check connections and try again."

    if not (1 <= selection <= len(detected)):
        if machine_mode:
            return (
                f"STATUS:ERROR|CODE:INVALID_SELECTION|"
                f"MESSAGE:Index_out_of_range_1-{len(detected)}"
            )
        else:
            return f"Error: Invalid selection. Please choose 1-{len(detected)}."

    # Get selected port and model
    port, scanner_model = detected[selection - 1]

    # If trying to connect to the current port, just return success
    if (
        port == current_port
        and current_ser
        and hasattr(current_ser, 'is_open')
        and current_ser.is_open
    ):
        if machine_mode:
            print(
                f"STATUS:OK|ACTION:SELECTED|PORT:{port}|MODEL:{scanner_model}"
            )
            return (
                current_ser,
                current_adapter,
                build_command_table(current_adapter, current_ser),
            )
        else:
            print(f"\nAlready connected to {port} ({scanner_model})")
            return (
                current_ser,
                current_adapter,
                *build_command_table(current_adapter, current_ser),
            )

    # Close current connection if it exists
    if current_ser and hasattr(current_ser, 'is_open') and current_ser.is_open:
        try:
            current_ser.close()
        except Exception as e:
            logger.error(f"Error closing current connection: {e}")

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
                new_ser.close()
                return f"STATUS:ERROR|CODE:NO_ADAPTER|MODEL:{scanner_model}"
            else:
                new_ser.close()
                return f"No adapter implemented for {scanner_model}."

        # Store the model in the adapter for reference
        new_adapter.model = scanner_model

        # Build new command table
        new_commands, new_command_help = build_command_table(
            new_adapter, new_ser
        )

        if machine_mode:
            print(
                f"STATUS:OK|ACTION:SELECTED|PORT:{port}|MODEL:{scanner_model}"
            )
        else:
            print(f"\nSuccessfully selected {port} ({scanner_model})")

        return (new_ser, new_adapter, new_commands, new_command_help)

    except Exception as e:
        logger.error(f"Error connecting to selected scanner: {e}")
        if machine_mode:
            error_msg = str(e).replace(" ", "_").replace(":", "_")
            return f"STATUS:ERROR|CODE:CONNECTION_FAILED|MESSAGE:{error_msg}"
        else:
            return f"Error connecting to scanner: {e}"


def handle_switch_command(
    ser, adapter, commands, command_help, machine_mode, args=None
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
        args (str, optional): Optional argument specifying scanner index.

    Returns:
        tuple or str: New connection or status message.
    """
    # In machine mode with an argument, treat it as a select command
    if args and args.strip():
        try:
            index = args.strip()
            result = select_scanner(index, ser, adapter, machine_mode)
            # If select_scanner returns a tuple, pass it through
            if isinstance(result, tuple) and len(result) == 4:
                return result
            # Otherwise, return the error message
            return result
        except Exception as e:
            logger.error(f"Error switching to scanner: {e}")
            if machine_mode:
                error_msg = str(e).replace(" ", "_").replace(":", "_")
                return f"STATUS:ERROR|CODE:SWITCH_FAILED|MESSAGE:{error_msg}"
            else:
                return f"Error switching to scanner: {e}"

    # Regular switch command
    result = switch_scanner(ser, adapter, machine_mode)
    if result:
        # Return the new connection info to be handled in main_loop
        return result
    return "Scanner switch canceled or failed"


def handle_list_command(machine_mode, ser=None, adapter=None):
    """
    List command handler for the scanner.

    Handler for the list command that shows all connected scanners.
    """
    return list_scanners(machine_mode, ser, adapter)


def handle_select_command(
    index, ser, adapter, commands, command_help, machine_mode
):
    """
    Select command handler for the scanner.

    Handler for the select command that selects a scanner by index.
    """
    result = select_scanner(index, ser, adapter, machine_mode)
    if isinstance(result, tuple) and len(result) == 4:
        return result
    return result


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
        # In machine mode, just scan and report but don't connect automatically
        detected = find_all_scanner_ports()
        if not detected:
            print("STATUS:ERROR|CODE:NO_SCANNERS_FOUND")
        else:
            print(f"STATUS:INFO|SCANNERS_FOUND:{len(detected)}")
            for idx, (port, model) in enumerate(detected, 1):
                print(f"SCANNER:{idx}|PORT:{port}|MODEL:{model}")
            print("STATUS:INFO|MESSAGE:Use_select_command_to_connect")
        return None, None, None, None
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
        if len(detected) == 1:
            selection = 1  # Auto-select if only one scanner in regular mode
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
