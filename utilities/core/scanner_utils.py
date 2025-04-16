"""
Core scanner utility functions.

This module provides essential functionality for scanner device interaction,
including detecting connected scanners, port scanning, and basic communication.
These core functions serve as building blocks for higher-level
scanner utilities.
"""

import logging
import time

import serial
from serial.tools import list_ports

# Import from core serial utilities - remove unused imports
from utilities.core.serial_utils import read_response, wait_for_data


def find_all_scanner_ports(
    baudrate=115200, timeout=0.5, max_retries=2, skip_ports=None
):
    """
    Find all connected scanner devices.

    Test communication on available ports.

    Args:
        baudrate: The serial connection speed to use
        timeout: Serial connection timeout in seconds
        max_retries: Number of retry attempts for detection
        skip_ports: List of ports to skip when scanning

    Returns:
        List of tuples (port_name, model_code) for detected scanners
    """
    if skip_ports is None:
        skip_ports = []

    detected = []
    retries = 0

    while retries < max_retries and not detected:
        ports = list(list_ports.comports())

        if not ports:
            logging.warning("No COM ports detected on this system")
            retries += 1
            time.sleep(1)
            continue

        # Log available ports for diagnostic purposes
        logging.info(f"Found {len(ports)} COM ports to check")
        for port_info in ports:
            logging.info(
                f"Available port: {port_info.device} - {port_info.description}"
            )

        for port_info in ports:
            port = port_info.device
            if port in skip_ports:
                logging.info(f"Skipping port: {port} (in skip list)")
                continue

            logging.info(f"Trying port: {port} ({port_info.description})")

            try:
                # Use longer timeouts for initial device detection
                with serial.Serial(
                    port, baudrate, timeout=timeout, write_timeout=0.5
                ) as ser:
                    time.sleep(0.1)  # Allow port to initialize

                    # Try MDL command to identify Uniden scanners
                    logging.info(f"Sending MDL to {port}")
                    ser.write(b"MDL\r")
                    wait_for_data(ser, max_wait=0.3)
                    model_response = read_response(ser)
                    logging.info(f"Response from {port}: {model_response}")

                    if model_response.startswith("MDL,"):
                        model_code = model_response.split(",")[1].strip()
                        detected.append((port, model_code))
                        continue

                    # Try alternative command if MDL doesn't work
                    ser.reset_input_buffer()
                    time.sleep(0.1)
                    logging.info(f"Sending WI to {port}")
                    ser.write(b"WI\r\n")
                    wait_for_data(ser, max_wait=0.3)
                    wi_response = read_response(ser)
                    logging.info(f"Response from {port}: {wi_response}")
                    if "AR-DV1" in wi_response:
                        detected.append((port, "AOR-DV1"))
            except Exception as e:
                logging.warning(f"Error testing port {port}: {str(e)}")

        if not detected:
            retries += 1
            if retries < max_retries:
                logging.info("No scanners found. Retrying in 3 seconds...")
                time.sleep(3)

    if not detected:
        logging.error("No scanners found after maximum retries.")

    return detected
