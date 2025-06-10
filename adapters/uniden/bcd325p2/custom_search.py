"""Custom search streaming functions for BCD325P2."""

import logging

from utilities.core.serial_utils import (
    read_response,
    send_command,
    wait_for_data,
)

logger = logging.getLogger(__name__)


def stream_custom_search(self, ser, record_count=1024):
    """Stream custom search results using the CSC command.

    Parameters
    ----------
    ser : serial.Serial
        Serial connection to the scanner.
    record_count : int, optional
        Number of result lines to read before stopping the stream.
        Defaults to 1024.

    Yields
    ------
    tuple
        ``(rssi, freq, sql)`` tuples as they are read from the scanner.
    """
    count = 0
    try:
        # Start streaming without the usual buffer flush delay
        send_command(ser, "CSC,ON", delay=0)
        while count < record_count:
            if not wait_for_data(ser, max_wait=0.5):
                break
            line = read_response(ser, timeout=1.0)
            if not line:
                break
            if not line.startswith("CSC,"):
                continue
            parts = line.split(",")
            if len(parts) >= 4:
                try:
                    rssi = int(parts[1])
                    freq = float(parts[2])
                    sql = int(parts[3])
                    yield (rssi, freq, sql)
                    count += 1
                except ValueError:
                    logger.debug(f"Malformed line: {line}")
        # Stop streaming and read final OK
        send_command(ser, "CSC,OFF", delay=0)
        read_response(ser, timeout=1.0)
    except Exception as e:
        logger.error(f"Error during custom search stream: {e}")
