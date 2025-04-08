"""
Script to migrate legacy scanner adapter modules to the new structure.

This tool helps automate the migration of adapter modules from the old
scanner_adapters folder to the new adapters folder with proper naming.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Map of legacy adapter paths to new paths
ADAPTER_MAPPING = {
    "scanner_adapters.baseAdapter": "adapters.base_adapter",
    "scanner_adapters.bc125atAdapter": "adapters.uniden.bc125at_adapter",
    # Add more mappings as needed
}

def find_legacy_adapters(directory=None):
    """Find all legacy adapter modules in the scanner_adapters directory"""
    if directory is None:
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    legacy_dir = os.path.join(directory, "scanner_adapters")
    if not os.path.exists(legacy_dir):
        print(f"Legacy adapters directory not found: {legacy_dir}")
        return []
    
    adapters = []
    for file in os.listdir(legacy_dir):
        if file.endswith(".py") and file != "__init__.py":
            adapters.append(os.path.join(legacy_dir, file))
    
    return adapters

def migrate_adapter(adapter_path, dry_run=True):
    """Migrate a single adapter to the new location"""
    filename = os.path.basename(adapter_path)
    module_name = os.path.splitext(filename)[0]
    
    # Determine new path based on naming convention
    # This is a simplified example - you'd need more logic for your specific case
    if module_name.endswith("Adapter"):
        # Convert camelCase to snake_case
        new_name = ''.join(['_'+c.lower() if c.isupper() else c for c in module_name])
        new_name = new_name.lstrip('_')
        if new_name.startswith("adapter_"):
            new_name = new_name[8:] + "_adapter"  # Move "adapter" to end
        elif not new_name.endswith("_adapter"):
            new_name += "_adapter"
    else:
        new_name = module_name
    
    # Determine manufacturer/brand if possible
    brand = "uniden" if "uniden" in module_name.lower() or "bc" in module_name.lower() else "generic"
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    new_dir = os.path.join(project_root, "adapters", brand)
    os.makedirs(new_dir, exist_ok=True)
    
    new_path = os.path.join(new_dir, f"{new_name}.py")
    
    if dry_run:
        print(f"Would migrate {adapter_path} to {new_path}")
    else:
        # Create the target directory if it doesn't exist
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        
        # Copy the file
        shutil.copy2(adapter_path, new_path)
        print(f"Migrated {adapter_path} to {new_path}")
        
        # Optionally update imports in the file
        # This would require parsing and modifying the Python code
    
    return new_path

def main():
    parser = argparse.ArgumentParser(description="Migrate legacy adapter modules to new structure")
    parser.add_argument("--directory", "-d", default=None, 
                        help="Directory containing the project (default: project root)")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    adapters = find_legacy_adapters(args.directory)
    
    if not adapters:
        print("No legacy adapters found to migrate.")
        return
    
    print(f"Found {len(adapters)} legacy adapter(s) to migrate.")
    
    for adapter in adapters:
        migrate_adapter(adapter, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
