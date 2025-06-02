"""
Timeout utilities for Scanner Controller.

This module provides tools for handling timeouts in operations.
"""

import logging
import threading

logger = logging.getLogger(__name__)


class ScannerTimeoutError(Exception):
    """Exception raised when an operation times out."""

    pass


def with_timeout(timeout_seconds, default_result=None):
    """
    Apply timeout to a function.

    Parameters:
        timeout_seconds (float): Maximum time in seconds to allow function to
        run.
        default_result: Value to return if timeout occurs, or raise
        TimeoutError if None.

    Returns:
        Function with timeout capability.
    """

    def timeout_function(func):
        def wrapper(*args, **kwargs):
            result = [default_result]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)

            if thread.is_alive():
                logger.warning(
                    f"Operation {func.__name__} timed out after "
                    f"{timeout_seconds} seconds"
                )
                if default_result is None:
                    raise ScannerTimeoutError(
                        f"Operation timed out after {timeout_seconds} seconds"
                    )
                return default_result

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper

    return timeout_function
