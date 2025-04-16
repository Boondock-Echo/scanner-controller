"""
Run flake8 with guaranteed .venv exclusion.

Use this script to run flake8 on all Python files in the project,
excluding the .venv directory and other specified directories.
"""

import os
import subprocess
import sys


def run_flake8():
    """Run flake8 with explicit exclusions for .venv directory."""
    # Path to project root (location of this script)
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Ensure we're in the project root
    os.chdir(project_root)

    # Build the list of files to check (excluding .venv)
    files_to_check = []
    for root, files in os.walk(project_root):
        # Skip .venv directory and other excluded directories
        if (
            '.venv' in root
            or 'venv' in root
            or '.git' in root
            or '__pycache__' in root
        ):
            continue

        # Add Python files to the list
        for file in files:
            if file.endswith('.py'):
                files_to_check.append(os.path.join(root, file))

    # Run flake8 on the filtered file list
    if files_to_check:
        cmd = [sys.executable, "-m", "flake8"] + files_to_check
        subprocess.run(cmd)
        print(f"Flake8 checked {len(files_to_check)} files.")
    else:
        print("No Python files found to check.")


if __name__ == "__main__":
    run_flake8()
