"""
Command loop module.

This module contains the main interactive command loop functionality.
"""

import logging

from utilities.command_parser import parse_command
from utilities.help_utils import show_help
from utilities.readlineSetup import initialize_readline
from utilities.scanner_manager import handle_switch_command

logger = logging.getLogger(__name__)


def main_loop(adapter, ser, commands, command_help, machine_mode=False):
    """
    REPL-style loop that prompts the user for commands and executes them.

    Parameters:
        adapter (object): Scanner adapter instance.
        ser (serial.Serial): Serial connection to the scanner.
        commands (dict): Dictionary of available commands.
        command_help (dict): Dictionary of help texts for commands.
        machine_mode (bool): Whether to use machine-friendly output.
            Defaults to False.
    """
    print("Type 'help' for a list of commands.\n")

    # Add switch scanner command
    # fmt: off
    commands["switch"] = (
        lambda _ser=ser, _adapter=adapter, _commands=commands,
        _command_help=command_help, _machine_mode=machine_mode:
        handle_switch_command(
            _ser, _adapter, _commands, _command_help, _machine_mode
        )
    )
    # fmt: on
    command_help["switch"] = "Switch to a different connected scanner"

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
            user_input = input("> ").strip()

            if user_input.lower() == "exit":
                break

            command, args = parse_command(user_input, commands)
            handler = commands.get(command)

            if handler:
                try:
                    result = handler(args) if args else handler()

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
                            lambda _ser=ser,
                            _adapter=adapter,
                            _commands=commands,
                            _command_help=command_help,
                            _machine_mode=machine_mode: handle_switch_command(
                                _ser,
                                _adapter,
                                _commands,
                                _command_help,
                                _machine_mode,
                            )
                        )
                        # fmt: on
                        command_help[
                            "switch"
                        ] = "Switch to a different connected scanner"
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
                            print(
                                "OK"
                                if not formatted_result.lower().startswith(
                                    "error"
                                )
                                else "ERROR"
                            )
                        else:
                            print(formatted_result)

                except Exception as e:
                    logger.error(f"Command error: {str(e)}", exc_info=True)
                    print(f"[Error] {e}")
            else:
                print("Unknown command. Type 'help' for options.")
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the program.")
        except Exception as e:
            logger.error(
                f"Unexpected error in command loop: {e}", exc_info=True
            )
            print(f"[Error] An unexpected error occurred: {e}")
