# readlineSetup.py

"""
Readline setup module.

Provides utilities for command line interface with tab completion.
"""


def initialize_readline(COMMANDS):
    """
    Initialize readline with tab completion for the given commands.

    Args:
        COMMANDS: Dictionary of available commands
    """
    try:
        import readline  # Unix and macOS
    except ImportError:
        try:
            import pyreadline3 as readline  # Windows with pyreadline3
        except ImportError:
            print(
                "Note: readline or pyreadline3 not available. "
                "Tab-completion disabled."
            )
            return

    def completer(text, state):
        """Complete command line text with tab completion.

        Dynamically filters commands and subcommands based on input.
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

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_history_length(100)
