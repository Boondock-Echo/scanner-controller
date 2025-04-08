#!/usr/bin/env python
import os
import sys
import importlib
import argparse

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def list_utilities():
    """List all available utilities in the subfolders"""
    utility_dirs = [
        'utilities/core',
        'utilities/commands',
        'utilities/tools',
        'utilities/research'
    ]
    
    print("Available utilities:")
    for dir_path in utility_dirs:
        full_path = os.path.join(script_dir, dir_path)
        if os.path.exists(full_path):
            print(f"\n{dir_path}/")
            for file in sorted(os.listdir(full_path)):
                if file.endswith('.py') and not file.startswith('__'):
                    print(f"  {file}")

def run_utility(utility_path, args):
    """Run a utility with the given arguments"""
    if not utility_path.endswith('.py'):
        utility_path += '.py'
    
    # Check common locations
    locations = [
        os.path.join(script_dir, utility_path),
        os.path.join(script_dir, 'utilities', utility_path),
        os.path.join(script_dir, 'utilities', 'core', utility_path),
        os.path.join(script_dir, 'utilities', 'commands', utility_path),
        os.path.join(script_dir, 'utilities', 'tools', utility_path),
        os.path.join(script_dir, 'utilities', 'research', utility_path)
    ]
    
    found_path = None
    for path in locations:
        if os.path.exists(path):
            found_path = path
            break
    
    if not found_path:
        print(f"Error: Could not find utility '{utility_path}'")
        return 1
    
    # Run the utility script
    print(f"Running: {found_path}")
    sys.argv = [found_path] + args
    
    # Execute the script
    with open(found_path) as f:
        script_code = f.read()
    exec(script_code, {'__file__': found_path})
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run utilities from their new location")
    parser.add_argument('utility', nargs='?', help='The utility script to run')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to pass to the utility')
    
    args = parser.parse_args()
    
    if not args.utility:
        list_utilities()
        sys.exit(0)
    
    sys.exit(run_utility(args.utility, args.args))
