"""
Scanner Controller main module.

This is the main entry point for the scanner controller application.
It provides command-line interface for interacting with various scanner models
through their respective adapters.
"""

# Standard library imports
import argparse
import logging

from utilities.command_loop import main_loop

# Local application/relative imports
from utilities.core.shared_utils import diagnose_connection_issues
from utilities.log_utils import configure_logging
from utilities.scanner_manager import detect_and_connect_scanner
from utilities.timeout_utils import ScannerTimeoutError

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
        default="WARNING",
        help="Set the logging level (default: WARNING)",
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
        # Detect and connect to scanner
        ser, adapter, commands, command_help = detect_and_connect_scanner(
            machine_mode
        )

        if not any([ser, adapter, commands, command_help]):
            # If connection was not successful
            if machine_mode:
                # In machine mode, we still proceed to the command loop
                # without a connection
                # Initialize empty command dictionaries
                commands = {}
                command_help = {}
                # The user will need to use list and select commands to connect
                logger.info(
                    "No scanner connected initially in machine mode, "
                    "continuing to command loop"
                )
            else:
                # In standard mode, we prompt for diagnostics and exit
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
        main_loop(adapter, ser, commands, command_help, machine_mode)

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
