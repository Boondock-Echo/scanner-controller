"""
Scanner Controller main module.

This is the main entry point for the scanner controller application.
It provides command-line interface for interacting with various scanner models
through their respective adapters.
"""

# Standard library imports
import argparse
import logging
import os
import sys

# Ensure that the root project directory is in the Python path.  This
# supports running the application from a variety of execution contexts
# without relying on package-level path manipulation.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

main_loop = None


# ------------------------------------------------------------------------------
# LOGGING SETUP
# ------------------------------------------------------------------------------

# Configure logging - will be set up in main() based on command line args


def main():
    """
    Start the Scanner Controller application.

    Parse command line arguments, detect and connect to a scanner,
    and launch the interactive command loop.
    """
    from utilities.command.loop import main_loop as _main_loop
    from utilities.core.shared_utils import diagnose_connection_issues
    from utilities.io.timeout_utils import ScannerTimeoutError
    from utilities.log_utils import configure_logging
    from utilities.scanner.manager import (
        connection_manager,
        detect_and_connect_scanner,
    )

    global main_loop
    if main_loop is None:
        main_loop = _main_loop

    # Parse CLI options
    parser = argparse.ArgumentParser(description="Scanner Interface")
    parser.add_argument(
        "--machine",
        action="store_true",
        help="Use machine-friendly output (no icons)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode to verify output formatting",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="CRITICAL",
        help="Set the logging level (default: CRITICAL)",
    )
    args = parser.parse_args()

    machine_mode = args.machine
    test_mode = args.test

    # Set up logging with user-specified level
    log_level = getattr(logging, args.log_level)
    logger = configure_logging(level=log_level)

    # Log the mode for verification
    if machine_mode:
        logger.info("Running in machine-friendly output mode")
        if test_mode:
            print("MACHINE_MODE: ENABLED")
    else:
        logger.info("Running in standard output mode")
        if test_mode:
            print("MACHINE_MODE: DISABLED")

    try:
        if machine_mode:
            # In machine mode, don't automatically detect scanner
            # Just start command loop with no scanner connected
            logger.info("Starting command loop without scanner in machine mode")
            print("STATUS:INFO|MESSAGE:Ready_for_commands")
            main_loop(connection_manager, None, None, {}, {}, machine_mode)
        else:
            # For normal mode, continue with automatic scanner detection
            # Detect and connect to scanner
            conn_id, ser, adapter, commands, command_help = (
                detect_and_connect_scanner(machine_mode)
            )

            if not all([ser, adapter, commands, command_help]):
                # If connection was not successful
                print(
                    "Failed to connect to scanner. Please check the connection "
                    "and try again."
                )
                if (
                    input(
                        "\nWould you like to run connection diagnostics?"
                        "(y/n): "
                    )
                    .lower()
                    .startswith("y")
                ):
                    diagnose_connection_issues()
                logger.error("Failed to connect to scanner. Exiting.")
                return

            # Start interactive command loop
            main_loop(
                connection_manager,
                adapter,
                ser,
                commands,
                command_help,
                machine_mode,
            )

    except ScannerTimeoutError:
        if machine_mode:
            print(
                "STATUS:ERROR|CODE:TIMEOUT|"
                "MESSAGE:Scanner_initialization_timeout"
            )
            logger.error("Timeout while initializing scanner adapter")
        else:
            print(
                "Timeout while initializing scanner adapter. Scanner"
                " may be unresponsive."
            )
            logger.error("Timeout while initializing scanner adapter")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        if machine_mode:
            # Provide structured error output for machine parsing
            error_msg = str(e).replace(" ", "_").replace(":", "_")
            print(f"STATUS:ERROR|CODE:EXCEPTION|MESSAGE:{error_msg}")
        else:
            print(f"Error: {e}")


# ------------------------------------------------------------------------------
# PROGRAM START
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
