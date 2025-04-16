"""
Utility script to identify and clean up legacy module redirections.

This tool helps identify where legacy module redirects are being used in the
codebase, making it easier to plan deprecation and removal of these redirects.
"""

# Standard library imports
import argparse
import os
import re
import sys

# Mapping of legacy modules to their new locations
LEGACY_MODULES = {
    "adapter_scanner.scanner_utils": "utilities.scanner_utils",
    "adapter_scanner.base_adapter": "adapters.base_adapter",
    # Add more legacy module mappings here
}


def find_legacy_usages(directory):
    """
    Recursively search for legacy module usages in the given directory.

    Args:
        directory (str): The directory to search in.

    Returns:
        dict: A dictionary where keys are legacy module names and values are
            lists of file paths where they are used.
    """
    legacy_usages = {module: [] for module in LEGACY_MODULES}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for legacy_module in LEGACY_MODULES:
                        if re.search(rf"\b{legacy_module}\b", content):
                            legacy_usages[legacy_module].append(file_path)

    return legacy_usages


def report_legacy_usages(usages):
    """
    Print a report of legacy module usages.

    Args:
        usages (dict): A dictionary where keys are legacy module names and
            values are lists of file paths where they are used.
    """
    for legacy_module, files in usages.items():
        if files:
            print(
                f"Legacy module '{legacy_module}' is used in the following "
                f"files:"
            )
            for file in files:
                print(f"  - {file}")
        else:
            print(
                f"Legacy module '{legacy_module}' is not used in the codebase."
            )


def main():
    """
    Execute the legacy module usage finder.

    Provides functionality for finding and reporting legacy module usages.
    """
    parser = argparse.ArgumentParser(
        description="Find and report on legacy module usages"
    )
    parser.add_argument(
        "--directory",
        "-d",
        default=None,
        help="Directory to scan (default: project root)",
    )
    parser.add_argument(
        "--report-file",
        "-o",
        help="Output report to this file instead of stdout",
    )

    args = parser.parse_args()

    # Use project root as default if no directory specified
    if args.directory is None:
        args.directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

    usages = find_legacy_usages(args.directory)

    if args.report_file:
        original_stdout = sys.stdout
        with open(args.report_file, "w") as f:
            sys.stdout = f
            report_legacy_usages(usages)
            sys.stdout = original_stdout
        print(f"Report written to {args.report_file}")
    else:
        report_legacy_usages(usages)


if __name__ == "__main__":
    main()
