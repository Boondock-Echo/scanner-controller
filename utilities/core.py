"""
Core utilities for scanner communications.

Shared functionality for sending commands, processing responses,
and ensuring data types are correct.
"""

import logging

logger = logging.getLogger(__name__)


def ensure_bytes(data):
    """Ensure data is in bytes format."""
    if isinstance(data, str):
        return data.encode('ascii')
    return data


def ensure_str(data):
    """Ensure data is in string format."""
    if isinstance(data, bytes):
        return data.decode('ascii')
    return data


def send_command(adapter, ser, command, parameter=None, raw=False):
    """Send command to the scanner and process the response."""
    # Implementation from the original send_command
    pass


def feedback(machine_mode, success, message):
    """Format feedback based on machine_mode setting."""
    if machine_mode:
        status = "OK" if success else "ERROR"
        # Convert spaces and special characters for easier parsing
        msg = str(message).replace(" ", "_").replace(":", "_")
        return f"STATUS:{status}|MESSAGE:{msg}"
    else:
        return message
