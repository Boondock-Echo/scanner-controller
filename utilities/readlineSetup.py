# readlineSetup.py

"""
Provides cross-platform readline support with tab-completion.
- On Unix/macOS: uses builtin readline
- On Windows: uses pyreadline3 (if installed)
- If neither is available, disables tab completion
"""

def initialize_readline(COMMANDS):
    """
    Sets up tab-completion for available COMMANDS.
    Parameters:
        COMMANDS (dict): dictionary of available command strings
    """
    try:
        import readline  # Unix and macOS
    except ImportError:
        try:
            import pyreadline3 as readline  # Windows with pyreadline3
        except ImportError:
            print("Note: readline or pyreadline3 not available. Tab-completion disabled.")
            return

    def completer(text, state):
        options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_history_length(100)
