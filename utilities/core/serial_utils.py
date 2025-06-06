"""
Serial utilities for scanner communication.

This module provides standardized functions for interacting with serial ports,
including:
- Clearing serial buffers
- Reading responses with timeout handling
- Sending commands with proper carriage return termination
- Waiting for data with configurable timeouts

These utilities handle error logging and consistent encoding/decoding to ensure
reliable communication with scanner devices.
"""

import logging
import time


def clear_serial_buffer(ser, delay=0.0):
    """Clear any accumulated data in the serial buffer before sending commands.

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
        while ser.in_waiting:
            ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")


def read_response(ser, timeout=1.0):
    r"""
    Read bytes from the serial port until a \r or \n are encountered.

    Args:
        ser: An open serial connection object
        timeout: Maximum time to wait for response in seconds

    Returns:
        The decoded response as a string, or empty string on error
    """
    response_bytes = bytearray()
    start_time = time.time()

    try:
        while (time.time() - start_time) < timeout:
            if ser.in_waiting > 0:
                byte = ser.read(1)
                if not byte:
                    break  # timeout reached
                if byte in b"\r\n":
                    break
                response_bytes.extend(byte)
            else:
                # Short sleep to avoid CPU spin
                time.sleep(0.01)

        # Decode the response
        response = response_bytes.decode("utf-8", errors="ignore").strip()
        logging.debug(f"Received response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error reading response: {e}")
        return ""


def send_command(ser, cmd, delay=0.0):
    """Clear the buffer and send a command (with CR termination) to the device.

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
        Response from the device as a string.
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

    Args:
        ser: An open serial connection object
        max_wait: Maximum time to wait in seconds

    Returns:
        True if data is available, otherwise False
    """
    start = time.time()
    while time.time() - start < max_wait:
        if ser.in_waiting:
            return True
        time.sleep(0.01)
    return False
