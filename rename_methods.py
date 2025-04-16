"""
This module converts mathod names.

CamelCase method names to snake_case
in Python files. It includes functions to process individual files or
entire directories.
"""

import os
import re

"""
Rename Methods module.

This module provides functionality related to rename methods.
"""


def convert_camel_to_snake(name):
    """
    Convert a camelCase string to snake_case.

    Args:
        name (str): The camelCase string.

    Returns:
        str: The converted snake_case string.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def process_file(filepath):
    """
    Process a Python file to convert camelCase method names to snake_case.

    Args:
        filepath (str): The path to the Python file.
    """
    with open(filepath, "r") as f:
        content = f.read()

    # Find all method definitions like "def camelCase"
    pattern = r"def ([a-z][a-zA-Z0-9]*)\("
    method_names = re.findall(pattern, content)

    # Filter to only get camelCase names (containing uppercase letters)
    camel_methods = [name for name in method_names if re.search(r"[A-Z]", name)]

    # Replace each camelCase method with snake_case
    for method in camel_methods:
        snake_method = convert_camel_to_snake(method)
        # Replace method definition
        content = re.sub(rf"def {method}\(", f"def {snake_method}(", content)
        # Replace method calls
        content = re.sub(rf"\.{method}\(", f".{snake_method}(", content)

    with open(filepath, "w") as f:
        f.write(content)


def scan_directory(directory):
    """
    Scan directories.

    Args:
        directory (str): The directory to scan.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                process_file(os.path.join(root, file))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=("Convert method names from camelCase to snake_case.")
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="Directory to scan (default: current working directory)",
    )
    args = parser.parse_args()

    scan_directory(args.directory)
    print("Method names converted from camelCase to snake_case")
