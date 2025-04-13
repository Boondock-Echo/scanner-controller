"""
Log Trim module.

This module provides functionality related to log trim.
"""

import logging
import os


def trim_log_file(log_file, max_size=1024 * 1024):
    """
    Trim the log file to ensure it does not exceed max_size bytes.

    Keep only the last max_size bytes of the file.
    """
    if not os.path.exists(log_file):
        return  # Do nothing if the file doesn't exist

    try:
        with open(log_file, "rb") as f:
            f.seek(0, 2)  # Move to the end of the file
            size = f.tell()
            if size <= max_size:
                return
            f.seek(-max_size, 2)  # Move to the last max_size bytes
            data = f.read()
        with open(log_file, "wb") as f:
            f.write(data)
        logging.info(f"Trimmed log file {log_file} to {max_size} bytes.")
    except Exception as e:
        logging.error(f"Error trimming log file {log_file}: {e}")
