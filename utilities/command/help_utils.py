"""
Help utilities for Scanner Controller.

This module contains functions for displaying help information
about available commands and features.
"""

import logging

from utilities.command.help_topics import get_extended_help

OTHER_COMMANDS = ["help", "list", "connect", "use", "close", "switch", "exit"]

logger = logging.getLogger(__name__)


def show_help(commands, command_help, command="", adapter=None):
    """
    Display help for a command or list all available commands.

    Parameters:
        commands (dict): Dictionary of available commands.
        command_help (dict): Dictionary of help texts for commands.
        command (str): Specific command to display help for.
        adapter (object): Scanner adapter instance.
    """
    # Display help for a specific command or topic
    if command:
        cmd = command.strip().lower()

        if cmd in command_help:
            print(f"\nHelp for '{cmd}':\n  {command_help[cmd]}")

        extended_help = get_extended_help(cmd)
        if extended_help:
            if cmd not in command_help:
                print(f"\nHelp for '{cmd}':")
            print(f"\n{extended_help}")
            return

        if cmd in command_help:
            return

        if adapter and hasattr(adapter, "get_help"):
            try:
                specific_help = adapter.get_help(command.upper())
                if specific_help:
                    print(
                        f"\n[{adapter.__class__.__name__}] help for"
                        f" '{command.upper()}':\n  {specific_help}"
                    )
                    return
            except Exception as e:
                print(f"[Error fetching device-specific help]: {e}")

        print(f"No help found for '{command}'.")
        return

    # Display general help (no specific command provided)

    print(
        """
================================================================================
    ██   ██ ███████ ██      ██████      ███    ███ ███████ ███    ██ ██    ██
    ██   ██ ██      ██      ██   ██     ████  ████ ██      ████   ██ ██    ██
    ███████ █████   ██      ██████      ██ ████ ██ █████   ██ ██  ██ ██    ██
    ██   ██ ██      ██      ██          ██  ██  ██ ██      ██  ██ ██ ██    ██
    ██   ██ ███████ ███████ ██          ██      ██ ███████ ██   ████  ██████
================================================================================
          """
    )

    # 1. General scanner commands (from adapter)
    # Define standard high-level commands that should be available
    standard_commands = {
        "Get Commands": [
            "get frequency",
            "get volume",
            "get squelch",
            "get mode",
            "get status",
            "get channel",
            "get system",
            "get backlight",
            "get battery",
        ],
        "Set Commands": [
            "set frequency",
            "set volume",
            "set squelch",
            "set mode",
            "set backlight",
            "set contrast",
        ],
        "Controlling Scanner": [
            "hold frequency",
            "send",
            "send key",
            "dump memory",
            "scan start",
            "scan stop",
            "band scope",
            "band sweep",
            "custom search",
        ],
        "Other": OTHER_COMMANDS,
    }

    # Check if any high-level commands exist in COMMANDS
    has_high_level_commands = any(
        cmd.startswith(
            (
                "get ",
                "set ",
                "hold ",
                "send",
                "dump ",
                "scan ",
                "band scope ",
                "band sweep ",
                "custom search ",
            )
        )
        for cmd in commands
    )

    # Use compact display format for both high-level and device-specific
    # commands
    if has_high_level_commands:
        general_commands = {
            "Get Commands": [
                cmd for cmd in sorted(commands) if cmd.startswith("get ")
            ],
            "Set Commands": [
                cmd for cmd in sorted(commands) if cmd.startswith("set ")
            ],
            "Controlling Scanner": [
                cmd
                for cmd in sorted(commands)
                if (
                    cmd.startswith("hold ")
                    or cmd == "send"
                    or cmd.startswith("send ")
                    or cmd.startswith("dump ")
                    or cmd.startswith("scan ")
                    or cmd.startswith("band scope")
                    or cmd.startswith("band sweep")
                    or cmd.startswith("custom search")
                )
            ],
            "Other": [
                cmd for cmd in standard_commands["Other"] if cmd in commands
            ],
        }

        # Ensure Controlling Scanner commands are always displayed if they exist
        if not general_commands["Controlling Scanner"]:
            general_commands["Controlling Scanner"] = [
                cmd
                for cmd in standard_commands["Controlling Scanner"]
                if cmd in commands
            ]
    else:
        general_commands = standard_commands

    # Process device-specific commands from adapter
    ds_categories = []
    command_groups = {}

    # Process adapter commands once
    ds_categories, command_groups = process_adapter_commands(
        adapter, general_commands
    )

    # Find longest category name across both high-level and device-specific
    # commands
    all_categories = list(general_commands.keys()) + ds_categories
    max_category_length = (
        max(len(name) for name in all_categories) if all_categories else 0
    )

    # Display high-level commands using the grid format with aligned colons
    print(
        """
                            High-Level Commands
--------------------------------------------------------------------------------
          """
    )
    cols_hl = 3  # Use 3 columns max for long command names

    for category, cmds in general_commands.items():
        if cmds:
            # Print category name with aligned colon
            print(f"{category:{max_category_length}}: ", end="")

            # Calculate indentation for wrapped lines
            indent = max_category_length + 2

            # Print commands in a grid with appropriate spacing
            sorted_cmds = sorted(cmds)
            for i, cmd in enumerate(sorted_cmds):
                print(f"{cmd:<15}", end="  ")

                # Add newline and indentation after every 3 commands
                if (i + 1) % cols_hl == 0:
                    print()
                    print(" " * indent, end="")

            print()  # Final newline for the category

    # 2. Device-specific commands from command libraries
    if command_groups:
        print("\n")
        print(
            """
              Device-Specific Commands:
--------------------------------------------------------------------------------
              """
        )

        # Display each category with aligned colons and consistent command
        # spacing
        cols = 5  # Number of columns in the grid

        for category_name in sorted(command_groups.keys()):
            commands_list = sorted(command_groups[category_name])
            if commands_list:
                # Print the category name with aligned colons using global max
                # length
                print(f"{category_name:{max_category_length}}: ", end="")

                # Calculate indentation for wrapped lines
                indent = (
                    max_category_length + 2
                )  # category length + colon + space

                # Print commands with consistent spacing
                for i, cmd in enumerate(commands_list):
                    print(
                        f"{cmd:4}", end="  "
                    )  # 4 chars for command + 2 spaces

                    # Add newline and indentation for wrapped lines
                    if (i + 1) % cols == 0 and i < len(commands_list) - 1:
                        print("\n" + " " * indent, end="")
                print()  # End line for category

    print("\nType 'help <command>' for details about a specific command.")


def process_adapter_commands(adapter, general_commands):
    """Process adapter commands and extract categories.

    Args:
        adapter: The scanner adapter instance
        general_commands: Dictionary of high-level commands

    Returns:
        tuple: (category_names, command_groups)
    """
    categories = []
    cmd_groups = {}

    if adapter and hasattr(adapter, "commands"):
        for cmd_name, cmd_obj in adapter.commands.items():
            # Skip commands already covered in general commands
            if any(
                cmd_name.lower() == gc.lower()
                for gc in sum(general_commands.values(), [])
            ):
                continue

            # Get category name
            if hasattr(cmd_obj, 'source_module') and cmd_obj.source_module:
                category_name = cmd_obj.source_module.replace('_', ' ').title()
                if category_name.endswith(" Commands"):
                    category_name = category_name[:-9]
            else:
                category_name = "Other"

            categories.append(category_name)

            if category_name not in cmd_groups:
                cmd_groups[category_name] = []
            cmd_groups[category_name].append(cmd_name)

    return categories, cmd_groups
