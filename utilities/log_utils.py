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


def configure_logging(log_file="scanner_controller.log", level=logging.INFO):
    """
    Configure logging for the scanner controller.

    Sets up a logging system that writes to both a file and the console. Creates
    the log directory if it doesn't exist. The file logger includes timestamps,
    while the console logger has a simpler format for readability.

    Parameters:
        log_file (str): Path to the log file. Defaults to
        "scanner_controller.log" in the current directory.
        level (int): Logging level threshold. Uses logging module constants:
                    DEBUG (10), INFO (20), WARNING (30), ERROR (40),
                    CRITICAL (50).
                    Defaults to logging.INFO.

    Returns:
        logging.Logger: The root logger configured with file
        and console handlers.

    Examples:
        >>> logger = configure_logging("app.log", logging.DEBUG)
        >>> logger.debug("Debug message")
        >>> logger.info("Info message")

        # With custom path
        >>> logger = configure_logging("logs/scanner.log")
        >>> logger.error("Error message")
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure file-based logging with timestamps and detailed information
    logging.basicConfig(
        filename=log_file,
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add console handler for immediate feedback during execution
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    # Return the root logger with both handlers attached
    return logging.getLogger("")


def get_logger(name=None):
    """
    Get a logger with the specified name.

    This is a convenience wrapper around logging.getLogger() that returns
    a logger with the specified name. If no name is provided, it returns
    the root logger.

    Parameters:
        name (str, optional): The name of the logger. If None,
        returns the root logger.

    Returns:
        logging.Logger: A logger instance with the specified name.

    Examples:
        >>> logger = get_logger("my_module")
        >>> logger.info("Module initialized")

        # Get the root logger
        >>> root_logger = get_logger()
        >>> root_logger.error("Application error")
    """
    return logging.getLogger(name)
