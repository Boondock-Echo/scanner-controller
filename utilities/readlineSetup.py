# readlineSetup.py

"""
Provide cross-platform tab-completion for command-line interfaces.

This module handles the setup of tab completion functionality to enhance the
user experience in command-line applications by allowing users to:
- Press TAB to see available commands
- Auto-complete partial command entries
- Navigate command history

Implementation details:
- On Unix/macOS: uses built-in readline module
- On Windows: uses pyreadline3 package (if installed)
- Falls back to basic input without completion if neither is available

Usage:
    from utilities.readlineSetup import initialize_readline
    initialize_readline(your_commands_dict)
"""


def initialize_readline(COMMANDS):
    """
    Set up tab-completion for available commands in a command-line interface.

    This function configures the readline environment to provide interactive
    command completion based on the provided command dictionary. It handles
    platform-specific readline implementations and gracefully degrades
    when neither is available.

    Parameters:
        COMMANDS (dict): Dictionary mapping command strings to their handler
                        functions.
                        The function docstrings are used to extract
                        subcommands.

    Returns:
        None: The function configures readline in-place and doesn't return
              a value.

    Note:
        Command handlers should have docstrings that list their
        subcommands/arguments for proper tab completion of second-level
        commands.
    """
    try:
        import readline  # Unix and macOS
    except ImportError:
        try:
            import pyreadline3 as readline  # Windows with pyreadline3
        except ImportError:
            print(
                "Note: readline or pyreadline3 not available."
                " Tab-completion disabled."
            )
            return

    def completer(text, state):
        """
        Complete command text for readline tab completion.

        Analyze the current input line and return appropriate completions based
        on:
        1. Top-level commands if at the beginning of input
        2. Subcommands/arguments if a valid command has already been entered

        Parameters:
            text (str): The text to complete (typically the partial word at
                      cursor)
            state (int): An index into the list of possible completions (0 for
                        first match)

        Returns:
            str or None: The completion string for the given state, or None if
                        no more completions
        """
        buffer = readline.get_line_buffer().strip()
        parts = buffer.split()

        # If no input or first word, suggest top-level commands
        if len(parts) == 0 or (len(parts) == 1 and not buffer.endswith(" ")):
            matches = [cmd for cmd in COMMANDS if cmd.startswith(text)]

        # If input contains a space, suggest subcommands or arguments
        elif len(parts) >= 1:
            command = parts[0].lower()
            if command in COMMANDS:
                # Get subcommands or arguments for the matched command
                subcommands = (
                    COMMANDS[command].__doc__.split()
                    if COMMANDS[command].__doc__
                    else []
                )
                matches = [sub for sub in subcommands if sub.startswith(text)]
            else:
                matches = []
        else:
            matches = []

        # Return the match for the current state
        try:
            return matches[state]
        except IndexError:
            return None

    # Configure readline settings
    readline.set_completer(completer)
    readline.parse_and_bind(
        "tab: complete"
    )  # Map tab key to completion function
    readline.set_history_length(100)  # Store last 100 commands in history
