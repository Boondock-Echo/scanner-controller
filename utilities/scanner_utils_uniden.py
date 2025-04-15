"""
Provide utilities for interacting with Uniden and AOR-DV1 scanners.

It includes functions for detecting scanner ports, sending commands, and
reading responses.
"""

import logging
import re
import time

import serial
from serial.tools import list_ports

# Configure logging
logging.basicConfig(
    filename="scanner_tool.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def clear_serial_buffer(ser):
    """
    Clear accumulated data in the serial buffer.

    This function clears the serial input and output buffers before sending
    commands.
    """
    ser.reset_input_buffer()
    ser.reset_output_buffer()


def read_response(ser, timeout=1.0):
    """
    Read bytes from the serial port until a carriage return.

    Reads a response from the serial port with a timeout.
    """
    ser.timeout = timeout
    response = ser.read_until(b"\r").decode("utf-8").strip()
    return response


def send_command(ser, cmd):
    """
    Clear the buffer and send a command (with CR termination) to a scanner.

    This function sends a command to the serial port and returns the response.
    """
    ser.write(f"{cmd}\r".encode("utf-8"))
    return read_response(ser)


def find_scanner_port(baudrate=115200, timeout=0.5, max_retries=2):
    """
    Scan all COM ports and return a list of tuples.

    - If the scanner responds to "MDL" with "MDL,[A-Za-z0-9,]+", it is treated
    as a Uniden-style scanner.
    - If the scanner responds to "WI" with "AR-DV1", it is treated as an AOR-DV1
    scanner.
    """
    detected = []
    retries = 0
    mdl_pattern = re.compile(r"^MDL,([A-Za-z0-9,]+)$")
    while retries < max_retries:
        ports = list_ports.comports()
        for port in ports:
            try:
                with serial.Serial(
                    port.device, baudrate, timeout=timeout
                ) as ser:
                    # Check for Uniden-style scanners
                    ser.write(b"MDL\r")
                    response = read_response(ser)
                    if mdl_pattern.match(response):
                        model_code = mdl_pattern.match(response).group(1)
                        detected.append((port.device, model_code, "uniden"))
                        continue

                    # Check for AOR-DV1 scanners
                    ser.write(b"WI\r")
                    response = read_response(ser)
                    if response.strip() == "AR-DV1":
                        detected.append((port.device, "AR-DV1", "aordv1"))
            except Exception:
                continue
        retries += 1
    return detected


def wait_for_data(ser, max_wait=0.3):
    """
    Wait up to max_wait seconds for incoming data on the serial port.

    Return True if data is available, otherwise False.
    """
    start = time.time()
    while time.time() - start < max_wait:
        if ser.in_waiting:
            return True
        time.sleep(0.01)
    return False
