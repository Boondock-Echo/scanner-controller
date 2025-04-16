#!/usr/bin/env python3
"""
Setup script for testing environment.

This script:
1. Creates necessary directories
2. Installs testing dependencies
3. Sets up pre-commit hooks
4. Generates adapter fix suggestions
"""
import importlib
import inspect
import os
import subprocess
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories for tests."""
    os.makedirs("logs", exist_ok=True)
    print("✓ Created logs directory")


def install_dependencies():
    """Install testing dependencies."""
    dependencies = ["pytest", "pytest-cov", "pytest-mock", "pre-commit"]

    print("Installing testing dependencies...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install"] + dependencies
    )
    print("✓ Installed testing dependencies")


def setup_pre_commit():
    """Set up pre-commit hooks."""
    if os.path.exists(".pre-commit-config.yaml"):
        print("Setting up pre-commit hooks...")
        subprocess.check_call(["pre-commit", "install"])
        print("✓ Installed pre-commit hooks")
    else:
        print("⚠ .pre-commit-config.yaml not found")


def generate_adapter_fixes():
    """Generate suggestions for fixing adapters."""
    print("\nChecking adapters for common issues...")

    # Add the project root to sys.path to allow importing modules
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

    try:
        # Try importing the adapters to check them
        adapters_to_check = [
            ("adapters.uniden.bc125at_adapter", "BC125ATAdapter", "BC125AT"),
            ("adapters.uniden.bcd325p2_adapter", "BCD325P2Adapter", "BCD325P2"),
            ("adapters.uniden.sds100_adapter", "SDS100Adapter", "SDS100"),
        ]

        for module_path, class_name, expected_mode in adapters_to_check:
            try:
                module = importlib.import_module(module_path)
                adapter_class = getattr(module, class_name, None)

                if adapter_class:
                    # Create an instance to test
                    try:
                        adapter = adapter_class()
                        if not hasattr(adapter, "machineMode"):
                            file_path = inspect.getfile(adapter_class)
                            rel_path = os.path.relpath(file_path, project_root)

                            print(
                                f"⚠ {class_name} missing 'machineMode' "
                                f"attribute"
                            )
                            print(f"  File: {rel_path}")
                            print(
                                f"  Fix: Add 'self.machineMode = "
                                f"'{expected_mode}'' to __init__ method\n"
                            )
                    except Exception as e:
                        print(f"⚠ Could not instantiate {class_name}: {e}")
            except ImportError:
                # This adapter module doesn't exist, skip it
                pass
    except Exception as e:
        print(f"Error checking adapters: {e}")


def main():
    """Execute the main setup procedure.

    Sets up the testing environment for Scanner Controller.
    """
    print("Setting up testing environment for Scanner Controller")
    print("=" * 50)

    create_directories()
    install_dependencies()
    setup_pre_commit()
    generate_adapter_fixes()

    print("\nSetup complete! You can now run tests with:")
    print("  pytest -xvs tests/")
    print("\nPre-commit hooks will run automatically on commit.")


if __name__ == "__main__":
    main()
