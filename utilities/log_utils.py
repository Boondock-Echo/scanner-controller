"""
Logging utilities for the scanner controller.

This module provides functions to configure and manage logging for the scanner
controller application. It sets up both file and console logging with
customizable log levels and formats.

Typical usage:
    logger = configure_logging(log_file="logs/app.log", level=logging.DEBUG)
    logger.info("Application started")
    logger.error("An error occurred")
"""

import logging
import os

from utilities.tools.log_trim import trim_log_file


def configure_logging(log_file=None, level=logging.INFO, max_size_mb=10):
    """
    Configure logging for the scanner controller.

    Sets up a logging system that writes to both a file and the console. Creates
    the log directory if it doesn't exist. The file logger includes timestamps,
    while the console logger has a simpler format for readability.

    Parameters:
        log_file (str): Path to the log file. If None, defaults to
                       "logs/scanner_tool.log" in the current directory.
        level (int): Logging level threshold. Uses logging module constants:
                    DEBUG (10), INFO (20), WARNING (30), ERROR (40),
                    CRITICAL (50).
                    Defaults to logging.INFO.
        max_size_mb (int): Maximum log file size in MB before trimming.
                          Defaults to 10MB.

    Returns:
        logging.Logger: The root logger configured with file
        and console handlers.

    Examples:
        >>> logger = configure_logging(level=logging.DEBUG)
        >>> logger.debug("Debug message")
        >>> logger.info("Info message")
    """
    # Set default log file if not provided
    if log_file is None:
        log_file = os.path.join("logs", "scanner_tool.log")

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Configure logging with file and console handlers
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    # Check if log file needs trimming
    max_size_bytes = max_size_mb * 1024 * 1024
    if os.path.exists(log_file) and os.path.getsize(log_file) > max_size_bytes:
        logging.info(f"Log file size exceeded {max_size_mb} MB. Trimming...")
        # Keep the log file manageable
        trim_log_file(log_file, max_size=max_size_bytes)

    logging.info("Logging setup complete.")

    # Return the root logger with both handlers attached
    return logging.getLogger("")


def get_logger(name, level=None):
    """
    Get a logger configured with proper formatting.

    Args:
        name (str): Logger name (usually __name__)
        level (str, optional): Logging level
                               (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                               If None, default to DEBUG for development

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)

    # Set default level to DEBUG if not specified
    if level is None:
        level = "DEBUG"  # Always debug by default for now

    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.DEBUG)
    logger.setLevel(numeric_level)

    # Ensure we have at least one handler
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
