"""
Analyze Unused Files module.

This script uses vulture to identify Python files in the project that contain
unused code or appear to be entirely unused. It generates a report listing
these files to help with code cleanup and maintenance.
"""

import argparse
import os
import subprocess


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Find unused Python files in a project."
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        ),
        help="Directory to analyze (default: project root)",
    )
    return parser.parse_args()


def find_python_files(directory, excluded_dirs=None):
    """Find Python files recursively.

    Searches the directory tree while skipping excluded directories.
    """
    python_files = []
    excluded_dirs = excluded_dirs or {"venv", "__pycache__", ".git"}
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def analyze_file_with_vulture(filepath):
    """Check a file for unused code.

    Uses the vulture tool to detect potentially unused code in the file.
    """
    try:
        result = subprocess.run(
            ["vulture", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # If vulture output is empty, the file has no unused code
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: vulture is not installed or not in PATH.")
        return None


def find_unused_files(directory):
    """Identify files where all code is unused."""
    python_files = find_python_files(directory)
    unused_files = []

    for file in python_files:
        print(f"Analyzing {file}...")
        vulture_output = analyze_file_with_vulture(file)
        if vulture_output and "unused" in vulture_output.lower():
            unused_files.append(file)

    return unused_files


def save_unused_files(unused_files, output_file="unused_files.txt"):
    """Save the list of unused files to a file."""
    with open(output_file, "w", encoding="utf-8") as file:
        for unused_file in sorted(unused_files):
            file.write(f"{unused_file}\n")
    print(f"\nUnused files saved to {output_file}")


if __name__ == "__main__":
    args = parse_arguments()
    project_dir = args.directory

    print(f"Analyzing directory: {project_dir}")
    unused_files = find_unused_files(project_dir)

    print("\nUnused Files:")
    for file in unused_files:
        print(file)

    # Save unused files to a file
    save_unused_files(unused_files)
