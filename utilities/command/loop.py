"""
Command loop module.

This module contains the main interactive command loop functionality.
"""

import logging

from utilities.command.help_utils import show_help
from utilities.command.parser import parse_command
from utilities.io.readline_setup import initialize_readline
from utilities.scanner.manager import (
    connect_to_scanner,
    handle_switch_command,
    scan_for_scanners,
)

logger = logging.getLogger(__name__)


def main_loop(adapter, ser, commands, command_help, machine_mode=False):
    """
    REPL-style loop that prompts the user for commands and executes them.

    Parameters:
        adapter (object): Scanner adapter instance, may be None in machine mode.
        ser (serial.Serial): Serial connection to the scanner, may be None in
            machine mode.
        commands (dict): Dictionary of available commands.
        command_help (dict): Dictionary of help texts for commands.
        machine_mode (bool): Whether to use machine-friendly output.
            Defaults to False.
    """
    if not machine_mode:
        print("Type 'help' for a list of commands.\n")
    else:
        print("STATUS:INFO|MESSAGE:Scanner_ready")

    # Initialize with basic commands
    if commands is None:
        commands = {}
    if command_help is None:
        command_help = {}

    # Add core commands that don't require a scanner connection
    commands["exit"] = lambda: "Exiting program"
    command_help["exit"] = "Exit the program"

    # Add machine mode specific commands
    if machine_mode:
        # Add scan command for discovering scanners
        commands["scan"] = scan_for_scanners
        command_help["scan"] = "Scan for available scanners"

        # Add connect command
        commands["connect"] = lambda scanner_id: connect_to_scanner(
            scanner_id, commands, command_help
        )
        command_help["connect"] = "Connect to a specific scanner by ID"

    # Only add scanner-specific commands if a scanner is connected
    if ser and adapter:
        # Add switch scanner command
        # fmt: off
        commands["switch"] = (
            lambda scanner_id=None,
            _ser=ser, _adapter=adapter, _commands=commands,
            _command_help=command_help,
            _machine_mode=machine_mode:
            handle_switch_command(
                _ser, _adapter, _commands, _command_help,
                _machine_mode, scanner_id
            )
        )
        # fmt: on
        command_help["switch"] = (
            "Switch to a different connected scanner. "
            "Optional: specify a scanner ID (e.g., 'switch 2')"
        )

    # Add help command
    # fmt: off
    commands["help"] = (
        lambda arg="", _commands=commands, _command_help=command_help,
        _adapter=adapter:
        show_help(
            _commands, _command_help, arg, _adapter
        )
    )
    # fmt: on

    # Initialize readline for command history and tab completion
    initialize_readline(commands)

    while True:
        try:
            if machine_mode:
                print("PROMPT:READY")

            user_input = input("> " if not machine_mode else "").strip()

            if user_input.lower() == "exit":
                if machine_mode:
                    print("STATUS:INFO|ACTION:EXIT")
                break

            command, args = parse_command(user_input, commands)
            handler = commands.get(command)

            if handler:
                try:
                    result = handler(args) if args else handler()

                    # Special handling for connect command result
                    if (
                        command == "connect"
                        and isinstance(result, tuple)
                        and len(result) == 4
                    ):
                        # Update references with the new connection
                        ser, adapter, new_commands, new_command_help = result

                        # Update commands dictionary with new scanner commands
                        commands.update(new_commands)
                        command_help.update(new_command_help)

                        # Re-add core commands
                        # Add switch scanner command
                        # fmt: off
                        commands["switch"] = (
                            lambda scanner_id=None,
                            _ser=ser, _adapter=adapter, _commands=commands,
                            _command_help=command_help,
                            _machine_mode=machine_mode:
                            handle_switch_command(
                                _ser, _adapter, _commands, _command_help,
                                _machine_mode, scanner_id
                            )
                        )
                        # fmt: on
                        command_help["switch"] = (
                            "Switch to a different connected scanner. "
                            "Optional: specify a scanner ID (e.g., 'switch 2')"
                        )

                        # Re-initialize readline with updated commands
                        initialize_readline(commands)
                        continue

                    # Special handling for switch command result
                    if (
                        command == "switch"
                        and isinstance(result, tuple)
                        and len(result) == 4
                    ):
                        ser, adapter, commands, command_help = result
                        # Re-inject help and switch commands after table rebuild
                        # fmt: off
                        commands["help"] = (
                            lambda arg="",
                            _commands=commands,
                            _command_help=command_help,
                            _adapter=adapter: show_help(
                                _commands, _command_help, arg, _adapter
                            )
                        )
                        # fmt: on
                        # fmt: off
                        commands["switch"] = (
                            lambda scanner_id=None, _ser=ser,
                            _adapter=adapter,
                            _commands=commands,
                            _command_help=command_help,
                            _machine_mode=machine_mode: handle_switch_command(
                                _ser,
                                _adapter,
                                _commands,
                                _command_help,
                                _machine_mode,
                                scanner_id
                            )
                        )
                        # fmt: on
                        command_help["switch"] = (
                            "Switch to a different connected scanner. "
                            "Optional: specify a scanner ID (e.g., 'switch 2')"
                        )
                        initialize_readline(commands)
                        continue

                    if result is not None:
                        if isinstance(result, bytes):
                            formatted_result = result.decode(
                                "ascii", errors="replace"
                            ).strip()
                        elif isinstance(result, (int, float)):
                            formatted_result = str(result)
                        else:
                            formatted_result = str(result)

                        if machine_mode:
                            # Check if result is already in machine-readable
                            # format
                            if formatted_result.startswith("STATUS:"):
                                print(formatted_result)
                            else:
                                is_error = formatted_result.lower().startswith(
                                    "error"
                                )
                                status = "ERROR" if is_error else "OK"
                                # Clean up the message for machine parsing
                                msg = formatted_result.replace(
                                    " ", "_"
                                ).replace(":", "_")
                                print(
                                    f"STATUS:{status}|COMMAND:{command}|"
                                    f"RESULT:{msg}"
                                )
                        else:
                            # For human-readable output, strip any machine
                            # format prefixes
                            if formatted_result.startswith("STATUS:"):
                                parts = formatted_result.split("|")
                                if len(parts) > 1:
                                    # Extract the message/result part
                                    for part in parts:
                                        if part.startswith(
                                            "MESSAGE:"
                                        ) or part.startswith("RESULT:"):
                                            value = part.split(":", 1)[
                                                1
                                            ].replace("_", " ")
                                            print(value)
                                            break
                                    else:
                                        print(formatted_result)
                                else:
                                    print(formatted_result)
                            else:
                                print(formatted_result)

                except Exception as e:
                    logger.error(f"Command error: {str(e)}", exc_info=True)
                    if machine_mode:
                        error_msg = str(e).replace(" ", "_").replace(":", "_")
                        print(
                            f"STATUS:ERROR|COMMAND:{command}|"
                            f"MESSAGE:{error_msg}"
                        )
                    else:
                        print(f"[Error] {e}")
            else:
                if machine_mode:
                    print(
                        f"STATUS:ERROR|CODE:UNKNOWN_COMMAND|COMMAND:{command}"
                    )
                else:
                    print("Unknown command. Type 'help' for options.")
        except KeyboardInterrupt:
            if machine_mode:
                print("STATUS:INFO|CODE:INTERRUPTED")
            else:
                print("\nUse 'exit' to quit the program.")
        except Exception as e:
            logger.error(
                f"Unexpected error in command loop: {e}", exc_info=True
            )
            if machine_mode:
                error_msg = str(e).replace(" ", "_").replace(":", "_")
                print(f"STATUS:ERROR|CODE:UNEXPECTED|MESSAGE:{error_msg}")
            else:
                print(f"[Error] An unexpected error occurred: {e}")
