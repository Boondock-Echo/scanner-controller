"""Generic command definitions for Uniden scanners."""

commands = {}


def get_help(command):
    """Return help text for ``command`` if available."""
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None


def list_commands():
    """Return a sorted list of available command names."""
    return sorted(commands.keys())
