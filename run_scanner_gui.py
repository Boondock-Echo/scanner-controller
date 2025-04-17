#!/usr/bin/env python3
"""
Scanner Controller Launcher.

This script provides a direct way to launch the Scanner GUI application
without dependency on Python's module system.

Usage:
    python run_scanner.py [--debug]
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys

# Import the logging utilities
from utilities.log_utils import configure_logging


def monkey_patch_serial():
    """Patch the serial module to add logging for better debugging."""
    import serial

    original_write = serial.Serial.write
    original_read = serial.Serial.read

    def patched_write(self, data):
        """Log all data written to serial port."""
        if isinstance(data, bytes):
            try:
                logging.debug(
                    f"SERIAL WRITE [{self.port}]: "
                    f"{data.decode('ascii', errors='replace')}"
                )
            except Exception:
                logging.debug(f"SERIAL WRITE [{self.port}]: {data}")
        return original_write(self, data)

    def patched_read(self, size=1):
        """Log all data read from serial port."""
        data = original_read(self, size)
        if data and len(data) > 0:
            try:
                logging.debug(
                    f"SERIAL READ [{self.port}]: "
                    f"{data.decode('ascii', errors='replace')}"
                )
            except Exception:
                logging.debug(f"SERIAL READ [{self.port}]: {data}")
        return data

    serial.Serial.write = patched_write
    serial.Serial.read = patched_read
    logging.debug("Serial port operations patched for debugging")


def clear_pycache():
    """Clear Python cache to ensure fresh imports."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for dirpath, dirnames, _ in os.walk(root_dir):
        if "__pycache__" in dirnames:
            cache_dir = os.path.join(dirpath, "__pycache__")
            try:
                shutil.rmtree(cache_dir)
                logging.debug(f"Cleared cache directory: {cache_dir}")
            except Exception as e:
                logging.warning(
                    f"Could not clear cache directory {cache_dir}: {e}"
                )


def main():
    """
    Launch the Scanner Controller.

    This function sets up logging, applies optional debugging patches,
    clears Python cache, and launches the Scanner GUI application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Scanner Controller")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    # Set up logging and debugging using the centralized logging utility
    level = logging.DEBUG if args.debug else logging.INFO
    log_file = os.path.join("logs", "scanner_controller.log")
    logger = configure_logging(log_file=log_file, level=level)

    # Log startup information
    debug_status = 'Yes' if args.debug else 'No'
    logger.info(f"Starting Scanner Controller (Debug={debug_status})")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running from: {os.path.dirname(os.path.abspath(__file__))}")

    # Apply monkey patching for debugging if requested
    if args.debug:
        monkey_patch_serial()

    # Clear Python cache to ensure fresh imports
    clear_pycache()

    # Get the directory of the current script
    repo_root = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(repo_root, "scanner_gui", "main.py")

    # Make sure we use the current repository modules
    sys.path.insert(0, repo_root)

    try:
        logger.info("Starting Scanner GUI application...")
        from scanner_gui.main import main

        main()
    except ImportError as e:
        logger.error(f"Import error: {e}")

        # Execute the script directly as a fallback
        try:
            logger.info("Attempting to run script directly...")
            cmd = [sys.executable, main_script]
            if args.debug:
                cmd.append("--debug")
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
        except Exception as e:
            logger.error(f"Error running script: {e}")
            logger.info("Please try running with: python -m scanner_gui")
            sys.exit(1)


if __name__ == "__main__":
    main()
