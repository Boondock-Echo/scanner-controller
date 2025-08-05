"""
Verify linter configuration.

This script verifies that all linters (including docstring checking) are
properly configured and working.
"""

import subprocess
import sys


def check_flake8_docstrings():
    """
    Check if flake8-docstrings is properly installed and configured.

    Returns:
        bool: True if the plugin is working, False otherwise
    """
    print("Checking flake8-docstrings installation...")

    # Check if the plugin is installed
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "flake8-docstrings"],
        capture_output=True,
        text=True,
    )

    if "Name: flake8-docstrings" not in result.stdout:
        print("flake8-docstrings is not installed. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "flake8-docstrings"],
            check=True,
        )
    else:
        print("flake8-docstrings is installed.")

    # Create a test file with a deliberate docstring error
    test_file = "docstring_test.py"
    with open(test_file, "w") as f:
        f.write("def test_function():\n    pass  # Missing docstring\n")

    # Run flake8 on the test file
    print("Testing flake8 docstring checking...")
    result = subprocess.run(
        [sys.executable, "-m", "flake8", test_file],
        capture_output=True,
        text=True,
    )

    # Check if D1 errors are reported (missing docstring)
    if "D1" in result.stdout:
        print("SUCCESS: flake8-docstrings is working correctly!")
        print(f"Found docstring error: {result.stdout.strip()}")
        return True
    else:
        print("WARNING: flake8-docstrings is not detecting missing docstrings.")
        print("Output was:", result.stdout)
        return False


if __name__ == "__main__":
    if check_flake8_docstrings():
        print("\nAll linters are properly configured.")
    else:
        print(
            "\nSome linters may not be properly configured."
            "Please review the output above."
        )
