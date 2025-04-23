"""
Command parsing utilities.

This module contains functions for parsing and processing user input commands.
"""

import logging

logger = logging.getLogger(__name__)


def parse_command(input_str, commands):
    """
    Parse user input into a command and its arguments.

    Parameters:
        input_str (str): User input string.
        commands (dict): Dictionary of available commands.

    Returns:
        tuple: Parsed command and arguments.

    Supports aliases: 'read' → 'get' and 'write' → 'set'.
    Attempts to match the longest prefix first (up to 3 words).
    """
    parts = input_str.strip().split()
    if not parts:
        return "", ""

    # Convert legacy read/write commands to get/set
    if parts[0].lower() == "read":
        parts[0] = "get"
    elif parts[0].lower() == "write":
        parts[0] = "set"

    for i in range(min(3, len(parts)), 0, -1):
        candidate = " ".join(parts[:i]).lower()
        if candidate in commands:
            logger.debug(
                f"Matched command: '{candidate}' with "
                f"args: '{' '.join(parts[i:])}'"
            )
            return candidate, " ".join(parts[i:])

    logger.debug(
        f"No matching command found for '{parts[0]}', treating as unknown "
        "command"
    )
    return parts[0].lower(), " ".join(parts[1:])
