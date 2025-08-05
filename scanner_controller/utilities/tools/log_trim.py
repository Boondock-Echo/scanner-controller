"""
Log Trim module.

This module provides functionality for managing log file sizes by trimming them
when they exceed specified size limits. This helps prevent logs from consuming
excessive disk space while maintaining the most recent log information.

The module preserves the most recent data in log files, which is typically the
most relevant for debugging recent issues.
"""

import logging
import os


def trim_log_file(log_file, max_size=1024 * 1024):
    """
    Trims the log file to ensure it does not exceed max_size bytes.

    This function checks the size of the specified log file and, if it exceeds
    the maximum size, trims it by keeping only the most recent data up to the
    maximum size. The function preserves the newest log entries (at the end of
    the file) and removes older entries from the beginning.

    Parameters:
        log_file (str): Path to the log file to be trimmed.
        max_size (int, optional): Maximum size in bytes for the log file.
                                  Defaults to 1MB (1024 * 1024 bytes).

    Returns:
        None

    Example:
        >>> trim_log_file("application.log")  # Trims to default 1MB
        >>> trim_log_file("debug.log", 5242880)  # Trims to 5MB

    Note:
        If an error occurs during trimming, it will be logged but not raised.
        The original file will remain unchanged in case of errors.
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
