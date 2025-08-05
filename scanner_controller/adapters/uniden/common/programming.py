"""
Uniden scanners programming mode functions.

Contains functions for entering and exiting programming mode.
"""

import functools
import logging
from contextlib import contextmanager

from .core import ensure_str

# Setup logger
logger = logging.getLogger(__name__)


def enter_programming_mode(self, ser):
    """Enter programming mode for Uniden scanners."""
    if hasattr(self, 'in_program_mode') and self.in_program_mode:
        logger.debug("Already in programming mode")
        return "Already in programming mode"

    try:
        logger.info("Entering programming mode...")
        response = self.send_command(ser, "PRG")
        response_str = ensure_str(response)
        if "OK" in response_str:
            self.in_program_mode = True
            logger.info("Successfully entered programming mode")
            return "Entered programming mode"
        logger.error(f"Failed to enter programming mode: {response_str}")
        return f"Failed to enter programming mode: {response_str}"
    except Exception as e:
        logger.exception(f"Exception while entering programming mode: {e}")
        return f"Error entering programming mode: {e}"


def exit_programming_mode(self, ser):
    """Exit programming mode for Uniden scanners."""
    if not hasattr(self, 'in_program_mode') or not self.in_program_mode:
        logger.debug("Not in programming mode")
        return "Not in programming mode"

    try:
        logger.info("Exiting programming mode...")
        response = self.send_command(ser, "EPG")
        response_str = ensure_str(response)
        if "OK" in response_str:
            self.in_program_mode = False
            logger.info("Successfully exited programming mode")
            return "Exited programming mode"
        logger.error(f"Failed to exit programming mode: {response_str}")
        return f"Failed to exit programming mode: {response_str}"
    except Exception as e:
        logger.exception(f"Exception while exiting programming mode: {e}")
        return f"Error exiting programming mode: {e}"


def requires_programming_mode(func):
    """
    Ensure the decorated function runs in programming mode.

    If not in programming mode, enter programming mode first.

    Usage:
        @requires_programming_mode
        def some_programming_function(self, ser, ...):
            # Run this only in programming mode
            ...
    """

    @functools.wraps(func)
    def wrapper(self, ser, *args, **kwargs):
        if not hasattr(self, 'in_program_mode') or not self.in_program_mode:
            logger.debug(
                f"Function {func.__name__} requires programming mode, "
                "entering now"
            )
            result = enter_programming_mode(self, ser)
            if "Error" in result or "Failed" in result:
                logger.error(
                    "Could not enter programming mode for "
                    f"{func.__name__}: {result}"
                )
                return result

        logger.debug(f"Executing programming mode function: {func.__name__}")
        return func(self, ser, *args, **kwargs)

    return wrapper


@contextmanager
def programming_session(self, ser):
    """
    Context manager for operations that need programming mode.

    Automatically handles entering and exiting programming mode.

    Usage:
        with self.programming_session(ser) as success:
            if success:
                # Do operations in programming mode
                ...
    """
    already_in_mode = hasattr(self, 'in_program_mode') and self.in_program_mode
    success = True

    if not already_in_mode:
        result = enter_programming_mode(self, ser)
        success = "Entered programming mode" in result

    try:
        yield success
    finally:
        if (
            not already_in_mode
            and hasattr(self, 'in_program_mode')
            and self.in_program_mode
        ):
            exit_programming_mode(self, ser)
