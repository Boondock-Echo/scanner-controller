"""
This module provides utility functions for serial communication.

Including clearing buffers, sending commands, and reading responses.
"""

import logging
import time


def clear_serial_buffer(ser, delay=0.2):
    """Clear accumulated data in the serial buffer before sending commands.

    Parameters
    ----------
    ser : serial.Serial
        Open serial connection to flush.
    delay : float, optional
        Seconds to pause before clearing.  ``0.2`` by default.
    """
    try:
        if delay:
            time.sleep(delay)
        while ser.in_waiting:
            ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")


def read_response(ser, timeout=1.0):
    r"""
    Read bytes from the serial port until a carriage return is encountered.

    This function continues reading until a timeout occurs or a carriage return
    is found.
    """
    response_bytes = bytearray()
    try:
        while True:
            byte = ser.read(1)
            if not byte:
                break  # timeout reached
            if byte in b"\r\n":
                break
            response_bytes.extend(byte)
        response = response_bytes.decode("utf-8", errors="ignore").strip()
        logging.debug(f"Received response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error reading response: {e}")
        return ""


def send_command(ser, cmd, delay=0.2):
    """Send a command to the scanner and return the response.

    Parameters
    ----------
    ser : serial.Serial
        Open connection to the scanner.
    cmd : str
        Command string to send.
    delay : float, optional
        Delay for :func:`clear_serial_buffer`.  Default ``0.2`` seconds.
    """
    clear_serial_buffer(ser, delay=delay)
    full_cmd = cmd.strip() + "\r"
    try:
        ser.write(full_cmd.encode("utf-8"))
        logging.info(f"Sent command: {cmd}")
    except Exception as e:
        logging.error(f"Error sending command {cmd}: {e}")
        return ""
    return read_response(ser)


def wait_for_data(ser, max_wait=0.3):
    """
    Wait up to max_wait seconds for incoming data on the serial port.

    Returns True if data is available, otherwise False.
    """
    start = time.time()
    while time.time() - start < max_wait:
        if ser.in_waiting:
            return True
        time.sleep(0.01)
    return False
