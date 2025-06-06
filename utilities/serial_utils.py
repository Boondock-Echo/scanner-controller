"""
This module provides utility functions for serial communication.

Including clearing buffers, sending commands, and reading responses.
"""

import logging
import time


def clear_serial_buffer(ser, delay=0.0):
    """Clear accumulated data in the serial buffer before sending commands.

    Parameters
    ----------
    ser : serial.Serial
        Open serial connection object.
    delay : float, optional
        Time to wait before flushing the buffer. Defaults to ``0`` seconds.
    """
    try:
        if delay:
            time.sleep(delay)
        if hasattr(ser, "reset_input_buffer"):
            ser.reset_input_buffer()
        else:
            while ser.in_waiting:
                ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")


def read_response(ser, timeout=1.0):
    r"""Read a response from the serial port with a timeout."""
    original_timeout = ser.timeout
    try:
        ser.timeout = timeout
        response = ser.read_until(b"\r").decode("utf-8").strip()
        logging.debug(f"Received response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error reading response: {e}")
        return ""
    finally:
        ser.timeout = original_timeout


def send_command(ser, cmd, delay=0.0):
    """Clear the buffer and send a command (with CR termination) to the scanner.

    Parameters
    ----------
    ser : serial.Serial
        Open serial connection object.
    cmd : str
        Command string to send.
    delay : float, optional
        Delay passed to :func:`clear_serial_buffer`. Defaults to ``0`` seconds.

    Returns
    -------
    str
        Response from the scanner.
    """
    clear_serial_buffer(ser, delay)
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
