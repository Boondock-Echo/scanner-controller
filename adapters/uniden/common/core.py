"""
Core utility functions for Uniden scanner adapters.

Contains common helper methods used by all Uniden scanner adapters.
"""

import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def ensure_bytes(data):
    """Convert to bytes if not already bytes."""
    if data is None:
        logger.debug("ensure_bytes: None value converted to empty bytes")
        return b""
    if isinstance(data, str):
        result = data.encode("ascii", errors="replace")
        if result != data.encode("ascii", errors="ignore"):
            logger.warning(f"Non-ASCII characters replaced in: {data!r}")
        return result
    logger.debug(f"ensure_bytes: Data already bytes type: {type(data)}")
    return data


def ensure_str(data):
    """Convert to string if not already a string."""
    if data is None:
        logger.debug("ensure_str: None value converted to empty string")
        return ""
    if isinstance(data, bytes):
        result = data.decode("ascii", errors="replace").strip()
        if result != data.decode("ascii", errors="ignore").strip():
            logger.warning(f"Non-ASCII bytes replaced in: {data!r}")
        return result
    logger.debug(f"ensure_str: Converting {type(data)} to string")
    return str(data)


def feedback(machine_mode, success, message):
    """Format feedback based on machine_mode setting."""
    if machine_mode:
        status = "OK" if success else "ERROR"
        # Clean up the message for machine parsing
        msg = str(message).replace(" ", "_").replace(":", "_")
        result = f"STATUS:{status}|MESSAGE:{msg}"
        logger.debug(f"Feedback in machine mode: {result}")
        return result
    logger.debug(f"Feedback in human mode: {message}")
    return message


def log_command_execution(func):
    """
    Log command execution with timing information.

    Log the command name, arguments, and execution time.

    Usage:
        @log_command_execution
        def some_command_function(self, ser, cmd, ...):
            # Log command execution
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        cmd = kwargs.get('cmd', args[2] if len(args) > 2 else 'Unknown')

        logger.debug(f"Executing command: {cmd}")
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Command {cmd} completed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.exception(
                f"Command {cmd} failed after {execution_time:.3f}s: {e}"
            )
            raise

    return wrapper


def document_ScannerCommand(command, description, examples=None, returns=None):
    """
    Decorate scanner command functions with documentation.

    Args:
        command: Specify the scanner command string (e.g., 'PRG', 'EPG').
        description: Provide a detailed description of the command's purpose.
        examples: Include optional usage examples.
        returns: Describe what the command returns.

    Usage:
        @document_ScannerCommand('PRG', 'Enter programming mode',
                                 examples=['PRG'],
                                 returns='OK if successful')
        def enter_programming_mode(self, ser):
            ...
    """

    def decorator(func):
        doc = func.__doc__ or ""

        # Build command documentation
        cmd_doc = f"\nCommand: {command}\n"
        cmd_doc += f"Description: {description}\n"

        if examples:
            cmd_doc += "Examples:\n"
            for example in examples:
                cmd_doc += f"  - {example}\n"

        if returns:
            cmd_doc += f"Returns: {returns}\n"

        # Add to function's docstring
        if doc:
            func.__doc__ = doc + cmd_doc
        else:
            func.__doc__ = cmd_doc

        return func

    return decorator


def validate_command(cmd, allowed_commands=None):
    """
    Validate that a command is properly formatted and in the allowed set.

    Args:
        cmd: Command string to validate
        allowed_commands: Optional list/set of allowed command strings

    Returns:
        cmd: The validated command

    Raises:
        ValueError: If cmd is empty or not in allowed_commands when specified
    """
    if not cmd or not cmd.strip():
        logger.error("Empty command provided")
        raise ValueError("Command cannot be empty")

    clean_cmd = cmd.strip().upper()

    if allowed_commands and clean_cmd not in allowed_commands:
        logger.error(
            f"Invalid command: {clean_cmd}. Must be one of {allowed_commands}"
        )
        raise ValueError(f"Command '{clean_cmd}' not in allowed command set")

    return clean_cmd


def format_response(response, pretty=False):
    """
    Format a scanner response for logging or display.

    Args:
        response: Raw response from the scanner
        pretty: Whether to format for human readability

    Returns:
        Formatted response string
    """
    if response is None:
        return "<No Response>"

    response_str = ensure_str(response)

    if not pretty:
        return response_str

    # Format for better human readability
    if "OK" in response_str:
        return f"SUCCESS: {response_str}"
    elif "ERR" in response_str or "ERROR" in response_str:
        return f"ERROR: {response_str}"
    else:
        lines = response_str.split('\n')
        if len(lines) > 1:
            return f"MULTI-LINE RESPONSE ({len(lines)} lines):\n" + response_str
        return f"RESPONSE: {response_str}"


