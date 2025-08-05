"""
Timeout utilities for Scanner Controller.

This module provides tools for handling timeouts in operations.
"""

import inspect
import logging
import threading
from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FutureTimeoutError,
)

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
        sig = inspect.signature(func)
        uses_stop_event = "stop_event" in sig.parameters

        def wrapper(*args, **kwargs):
            stop_event = threading.Event()

            def call_func():
                if uses_stop_event:
                    kwargs_with_event = dict(kwargs)
                    kwargs_with_event["stop_event"] = stop_event
                    return func(*args, **kwargs_with_event)
                return func(*args, **kwargs)

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(call_func)
                try:
                    return future.result(timeout=timeout_seconds)
                except FutureTimeoutError:
                    logger.warning(
                        f"Operation {func.__name__} timed out after {timeout_seconds} seconds"
                    )
                    stop_event.set()
                    future.cancel()
                    if default_result is None:
                        raise ScannerTimeoutError(
                            f"Operation timed out after {timeout_seconds} seconds"
                        )
                    return default_result
                except Exception as exc:
                    raise exc

        return wrapper

    return timeout_function
