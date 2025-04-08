#!/usr/bin/env python3
"""
Setup script for testing environment

This script:
1. Creates necessary directories
2. Installs testing dependencies
3. Sets up pre-commit hooks
"""
import os
import subprocess
import sys

def create_directories():
    """Create necessary directories for tests"""
    os.makedirs('logs', exist_ok=True)
    print("✓ Created logs directory")

def install_dependencies():
    """Install testing dependencies"""
    dependencies = [
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'pre-commit',
    ]
    
    print("Installing testing dependencies...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + dependencies)
    print("✓ Installed testing dependencies")

def setup_pre_commit():
    """Set up pre-commit hooks"""
    if os.path.exists('.pre-commit-config.yaml'):
        print("Setting up pre-commit hooks...")
        subprocess.check_call(['pre-commit', 'install'])
        print("✓ Installed pre-commit hooks")
    else:
        print("⚠ .pre-commit-config.yaml not found")

def main():
    """Main setup function"""
    print("Setting up testing environment for Scanner Controller")
    print("=" * 50)
    
    create_directories()
    install_dependencies()
    setup_pre_commit()
    
    print("\nSetup complete! You can now run tests with:")
    print("  pytest -xvs tests/")
    print("\nPre-commit hooks will run automatically on commit.")

if __name__ == "__main__":
    main()
