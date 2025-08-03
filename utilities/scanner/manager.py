"""Scanner management utilities.

This module contains functions for managing scanner connections and switching.
"""

import logging

import serial  # noqa: F401

from utilities.scanner.backend import find_all_scanner_ports
from utilities.scanner.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

# Global connection manager instance
connection_manager = ConnectionManager()


def detect_and_connect_scanner(machine_mode=False):
    """Detect available scanners and connect to one selected by the user.

    Parameters
    ----------
    machine_mode : bool
        Whether to use machine-friendly output.

    Returns
    -------
    tuple
        (conn_id, ser, adapter, commands, command_help) or
        (None, None, None, None, None) if failed
    """
    if machine_mode:
        print("STATUS:INFO|ACTION:SCANNING_FOR_DEVICES")
    else:
        print("Searching for connected scanners...")

    skip_ports = [
        ser.port for _, (ser, _, _, _) in connection_manager.list_all()
    ]
    detected = find_all_scanner_ports(skip_ports=skip_ports)

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
        return None, None, None, None, None

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
                    return None, None, None, None, None
            except ValueError:
                print("Invalid input. Exiting.")
                return None, None, None, None, None

        if 1 <= selection <= len(detected):
            port, scanner_model = detected[selection - 1]
        else:
            if machine_mode:
                print("STATUS:ERROR|CODE:INVALID_SELECTION")
            else:
                print("Invalid selection.")
            return None, None, None, None, None
    except ValueError:
        print("Invalid input. Exiting.")
        return None, None, None, None, None

    try:
        conn_id = connection_manager.open_connection(
            port, scanner_model, machine_mode
        )
        ser, adapter, commands, command_help = connection_manager.get(conn_id)

        if machine_mode:
            print(
                f"STATUS:OK|ACTION:CONNECTED|PORT:{port}|"
                f"MODEL:{scanner_model}|ID:{conn_id}"
            )
        else:
            print(f"Connected to {port} ({scanner_model}) [ID {conn_id}]")

        return conn_id, ser, adapter, commands, command_help

    except Exception as e:
        logger.error(f"Error communicating with scanner: {e}")
        if machine_mode:
            error_msg = str(e).replace(" ", "_").replace(":", "_")
            print(f"STATUS:ERROR|CODE:COMMUNICATION_FAILED|MESSAGE:{error_msg}")
        else:
            print(f"Error communicating with scanner: {e}")
        return None, None, None, None, None


def scan_for_scanners():
    """Scan for available scanners and return the list.

    This command is primarily for machine mode to list scanners
    without automatically connecting.

    Returns
    -------
    str
        Machine-readable list of available scanners
    """
    logger.info("Scanning for connected scanners")

    skip_ports = [
        ser.port for _, (ser, _, _, _) in connection_manager.list_all()
    ]
    detected = find_all_scanner_ports(skip_ports=skip_ports)

    if not detected:
        return "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"

    result = f"STATUS:OK|SCANNERS_FOUND:{len(detected)}"
    for idx, (port, model) in enumerate(detected, 1):
        result += f"|SCANNER:{idx}|PORT:{port}|MODEL:{model}"

    return result


def connect_to_scanner(
    connection_manager,
    scanner_id,
    machine_mode=True,
    existing_commands=None,
    existing_command_help=None,
    skip_ports=None,
):
    """Connect to a specific scanner by its ID.

    Parameters
    ----------
    connection_manager : ConnectionManager
        Manager instance used to open and track the connection.
    scanner_id : str
        Scanner ID from the scan results.
    machine_mode : bool, optional
        Whether to initialize the adapter in machine mode. Defaults to True.
    existing_commands : dict, optional
        Existing commands dictionary to update.
    existing_command_help : dict, optional
        Existing command help dictionary to update.
    skip_ports : list[str], optional
        Serial ports that should be skipped when scanning.

    Returns
    -------
    tuple
        ``(ser, adapter, commands, command_help)`` if successful, or an
        error message string if failed.
    """
    try:
        scanner_id = int(scanner_id)
    except ValueError:
        return (
            "STATUS:ERROR|CODE:INVALID_SCANNER_ID|"
            "MESSAGE:Scanner_ID_must_be_a_number"
        )

    if skip_ports is None:
        skip_ports = [
            ser.port for _, (ser, _, _, _) in connection_manager.list_all()
        ]
    # Get the list of available scanners
    detected = find_all_scanner_ports(skip_ports=skip_ports)

    if not detected:
        return "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"

    if not (1 <= scanner_id <= len(detected)):
        return f"STATUS:ERROR|CODE:INVALID_SCANNER_ID|MAX_ID:{len(detected)}"

    # Get the selected scanner
    port, scanner_model = detected[scanner_id - 1]

    try:
        conn_id = connection_manager.open_connection(
            port, scanner_model, machine_mode
        )
        ser, adapter, commands, command_help = connection_manager.get(conn_id)

        if existing_commands is not None and existing_command_help is not None:
            # Placeholder for merging logic if needed
            pass

        return ser, adapter, commands, command_help

    except Exception as e:
        logger.error(f"Error communicating with scanner: {e}")
        error_msg = str(e).replace(" ", "_").replace(":", "_")
        return f"STATUS:ERROR|CODE:COMMUNICATION_FAILED|MESSAGE:{error_msg}"


def switch_scanner(
    connection_manager,
    scanner_id,
    machine_mode=True,
    connect_func=connect_to_scanner,
):
    """Close the active connection and connect to a new scanner by ID.

    Parameters
    ----------
    connection_manager : ConnectionManager
        Manager instance used to manage the connections.
    scanner_id : str or int
        Identifier of the scanner to switch to.
    machine_mode : bool, optional
        Whether to use machine-friendly output. Defaults to True.

    Returns
    -------
    tuple or str
        Result of :func:`connect_to_scanner`.
    """
    if connection_manager.active_id is not None:
        connection_manager.close_connection(connection_manager.active_id)
    skip_ports = [
        ser.port for _, (ser, _, _, _) in connection_manager.list_all()
    ]
    return connect_func(
        connection_manager,
        scanner_id,
        machine_mode=machine_mode,
        skip_ports=skip_ports,
    )
