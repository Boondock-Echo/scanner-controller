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
    scan_for_scanners,
    switch_scanner,
)

logger = logging.getLogger(__name__)


def main_loop(
    connection_manager,
    adapter=None,
    ser=None,
    commands=None,
    command_help=None,
    machine_mode=False,
):
    """Interactive REPL for executing scanner commands.

    Parameters
    ----------
    connection_manager : ConnectionManager
        Manager instance tracking all open connections.
    adapter : object, optional
        Scanner adapter instance for an initial connection.
    ser : serial.Serial, optional
        Serial connection for an initial scanner.
    commands : dict, optional
        Dictionary of available commands for the active connection.
    command_help : dict, optional
        Help text for commands.
    machine_mode : bool, optional
        Whether to use machine-friendly output. Default ``False``.
    """
    if not machine_mode:
        print("Type 'help' to display the help menu.\n")
    else:
        print("STATUS:INFO|MESSAGE:Scanner_ready")

    global_commands = {}
    global_help = {}

    def refresh_active():
        nonlocal commands, command_help, adapter, ser
        commands = dict(global_commands)
        command_help = dict(global_help)
        conn = connection_manager.get()
        if conn:
            ser, adapter, conn_cmds, conn_help = conn
            commands.update(conn_cmds)
            command_help.update(conn_help)
        initialize_readline(commands)

    if commands is None:
        commands = {}
    if command_help is None:
        command_help = {}

    global_commands.update(commands)
    global_help.update(command_help)

    global_commands["exit"] = lambda: "Exiting program"
    global_help["exit"] = "Exit the program"

    def list_connections():
        conns = connection_manager.list_all()
        if not conns:
            return "No connections"
        if machine_mode:
            result = f"STATUS:OK|CONNECTIONS:{len(conns)}"
            for cid, (s, _, _, _) in conns:
                active = 1 if cid == connection_manager.active_id else 0
                port = getattr(s, "port", "unknown")
                result += f"|CONNECTION:{cid}|PORT:{port}|ACTIVE:{active}"
            return result
        lines = []
        for cid, (s, _, _, _) in conns:
            mark = "*" if cid == connection_manager.active_id else " "
            port = getattr(s, "port", "unknown")
            lines.append(f"[{cid}]{mark} {port}")
        return "\n".join(lines)

    def connect_cmd(scanner_id):
        result = connect_to_scanner(
            connection_manager, scanner_id, machine_mode=machine_mode
        )
        if isinstance(result, tuple):
            refresh_active()
            conn_id = connection_manager.active_id
            ser_, _, _, _ = connection_manager.get()
            if machine_mode:
                return (
                    f"STATUS:OK|ACTION:CONNECTED|ID:{conn_id}|PORT:{ser_.port}"
                )
            return f"Connected to {ser_.port} [ID {conn_id}]"
        return result

    def use_cmd(cid):
        try:
            cid = int(cid)
        except ValueError:
            return "Invalid connection ID"
        try:
            connection_manager.active_id = cid
        except KeyError:
            return f"Connection {cid} not found"
        refresh_active()
        if machine_mode:
            return f"STATUS:OK|ACTION:ACTIVE|ID:{cid}"
        return f"Using connection {cid}"

    def close_cmd(cid):
        try:
            cid = int(cid)
        except ValueError:
            return "Invalid connection ID"
        connection_manager.close_connection(cid)
        refresh_active()
        if machine_mode:
            return f"STATUS:OK|ACTION:CLOSED|ID:{cid}"
        return f"Closed connection {cid}"

    def scan_cmd(_arg=None):
        result = scan_for_scanners()
        if machine_mode:
            return result
        if result.startswith("STATUS:ERROR"):
            return "No scanners found"
        parts = result.split("|")[1:]  # drop STATUS
        scanners = []
        current = {}
        for part in parts:
            if ":" not in part:
                continue
            key, val = part.split(":", 1)
            if key == "SCANNER":
                if current:
                    scanners.append(current)
                current = {"id": val}
            elif key == "PORT":
                current["port"] = val
            elif key == "MODEL":
                current["model"] = val
        if current:
            scanners.append(current)
        lines = [
            f"  {s['id']}. {s.get('port', '')} — {s.get('model', '')}"
            for s in scanners
        ]
        return "\n".join(lines)

    def switch_cmd(scanner_id):
        result = switch_scanner(
            connection_manager,
            scanner_id,
            machine_mode=machine_mode,
            connect_func=connect_to_scanner,
        )
        if isinstance(result, tuple):
            refresh_active()
            conn_id = connection_manager.active_id
            ser_, _, _, _ = connection_manager.get()
            if machine_mode:
                return (
                    f"STATUS:OK|ACTION:CONNECTED|ID:{conn_id}|PORT:{ser_.port}"
                )
            return f"Connected to {ser_.port} [ID {conn_id}]"
        return result

    global_commands.update(
        {
            "list": lambda: list_connections(),
            "scan": lambda: scan_cmd(),
            "connect": lambda arg: connect_cmd(arg),
            "use": lambda arg: use_cmd(arg),
            "close": lambda arg: close_cmd(arg),
            "switch": lambda arg: switch_cmd(arg),
        }
    )
    global_help.update(
        {
            "list": "List open connections",
            "scan": "Detect connected scanners",
            "connect": "Connect to scanner ID from 'scan'",
            "use": "Select active connection",
            "close": "Close a connection",
            "switch": "Close current connection before opening another",
        }
    )

    refresh_active()

    global_commands["help"] = lambda arg="": show_help(
        commands, command_help, arg, adapter
    )
    global_help["help"] = "Show this help message"
    refresh_active()

    while True:
        try:
            if machine_mode:
                print("PROMPT:READY")

            user_input = input("> " if not machine_mode else "").strip()

            if user_input.lower() == "exit":
                if machine_mode:
                    print("STATUS:INFO|ACTION:EXIT")
                break

            command, args = parse_command(
                user_input, commands, connection_manager
            )
            handler = commands.get(command)

            if handler:
                try:
                    result = handler(args) if args else handler()

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
                            if formatted_result.startswith("STATUS:"):
                                print(formatted_result)
                            else:
                                is_error = formatted_result.lower().startswith(
                                    "error"
                                )
                                status = "ERROR" if is_error else "OK"
                                msg = formatted_result.replace(
                                    " ", "_"
                                ).replace(":", "_")
                                print(
                                    f"STATUS:{status}|COMMAND:{command}|"
                                    f"RESULT:{msg}"
                                )
                        else:
                            if formatted_result.startswith("STATUS:"):
                                parts = formatted_result.split("|")
                                for part in parts:
                                    if part.startswith(
                                        "MESSAGE:"
                                    ) or part.startswith("RESULT:"):
                                        value = part.split(":", 1)[1].replace(
                                            "_", " "
                                        )
                                        print(value)
                                        break
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
