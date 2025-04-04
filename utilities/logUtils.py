import os

def trim_log_file(filepath, max_lines=1500):
    """
    Trims the log file to keep only the most recent `max_lines` lines.

    Args:
        filepath (str): Path to the log file.
        max_lines (int): Maximum number of lines to retain.
    """
    if not os.path.exists(filepath):
        return  # Do nothing if the file doesn't exist

    with open(filepath, 'r') as file:
        lines = file.readlines()

    if len(lines) > max_lines:
        with open(filepath, 'w') as file:
            file.writelines(lines[-max_lines:])
